import streamlit as st
import os
from supabase import create_client
import pandas as pd
import random

# --- CONFIGURACIÓN Y CONEXIÓN ---
def get_secret(key):
    return st.secrets[key] if key in st.secrets else os.environ.get(key)

url = get_secret('PROJECT_URL').strip().rstrip('/')
key = get_secret('API_SUPABASE').strip()
supabase = create_client(url, key)

st.set_page_config(page_title="Reptile Logistics Pro", layout="wide", page_icon="🐍")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; background-color: #005088; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🐍 Reptile Logistics Pro")
    username = st.text_input("Nombre del Propietario")
    if st.button("Entrar al Sistema"):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.rerun()
    st.stop()

# --- PANEL LATERAL ---
st.sidebar.title(f"👤 {st.session_state.username}")
menu = st.sidebar.radio("Navegación", ["Panel de Control", "Nuevo Ejemplar"])
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# --- LÓGICA: REGISTRO ---
if menu == "Nuevo Ejemplar":
    st.header("➕ Registro de Nuevo Ejemplar")
    with st.form("registro_form"):
        col1, col2 = st.columns(2)
        with col1:
            especie = st.text_input("Especie")
            sex = st.selectbox("Sexo", ["Macho", "Hembra", "Desconocido"])
        with col2:
            peso = st.number_input("Peso Inicial (g)", min_value=0, step=1)
            fecha = st.date_input("Fecha de Registro")
        
        notas = st.text_area("Notas / Historial")
        
        if st.form_submit_button("Guardar en Base de Datos"):
            u_id = f"{especie[:2].upper()}-{random.randint(1000, 9999)}"
            data = {
                "unique_id": u_id,
                "owner_name": st.session_state.username,
                "species": especie,
                "sex": sex,
                "peso": int(peso),
                "notas": notas
            }
            try:
                supabase.table("reptiles").insert(data).execute()
                st.success(f"Ejemplar {u_id} registrado correctamente.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# --- LÓGICA: PANEL DE CONTROL ---
elif menu == "Panel de Control":
    st.header("📊 Panel de Gestión")
    
    try:
        res = supabase.table("reptiles").select("*").eq("owner_name", st.session_state.username).execute()
        reptiles = res.data
        
        if not reptiles:
            st.info("No tienes ejemplares aún.")
        else:
            options = {r['unique_id']: r for r in reptiles}
            sel_id = st.selectbox("Selecciona un ejemplar:", list(options.keys()))
            data_sel = options[sel_id]
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Especie", data_sel.get('species', '-'))
            c2.metric("Sexo", data_sel.get('sex', '-'))
            c3.metric("Peso", f"{data_sel.get('peso', 0)} g")
            
            st.markdown("---")
            st.subheader("Tendencia de Peso")
            # Gráfica básica
            df = pd.DataFrame({'Día': ['Inicio', 'Actual'], 'Peso (g)': [data_sel.get('peso', 0)-5, data_sel.get('peso', 0)]})
            st.line_chart(df.set_index('Día'))
            
            with st.expander("Detalles Médicos"):
                st.write(data_sel.get('notas', 'Sin notas.'))
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
