import streamlit as st
import os
from supabase import create_client
import pandas as pd
import random

# --- CONFIGURACIÓN ---
def get_secret(key):
    return st.secrets[key] if key in st.secrets else os.environ.get(key)

# Inicialización
url = get_secret('PROJECT_URL').strip().rstrip('/')
key = get_secret('API_SUPABASE').strip()
supabase = create_client(url, key)

st.set_page_config(page_title="Reptile Logistics Pro", layout="wide", page_icon="🐍")

# --- ESTILOS PROFESIONALES ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #005088; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🐍 Reptile Logistics Pro")
    st.subheader("Acceso al Sistema de Gestión")
    with st.form("login"):
        username = st.text_input("Nombre del Propietario")
        if st.form_submit_button("Entrar al Dashboard"):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
    st.stop()

# --- PANEL LATERAL ---
st.sidebar.title(f"👤 {st.session_state.username}")
menu = st.sidebar.radio("Navegación", ["Panel de Control", "Nuevo Ejemplar"])
st.sidebar.markdown("---")
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
            peso = st.number_input("Peso Inicial (g)", min_value=0.0)
            fecha = st.date_input("Fecha de Registro")
        
        notas = st.text_area("Notas / Historial")
        
        if st.form_submit_button("Guardar en Base de Datos"):
            u_id = f"{especie[:2].upper()}-{random.randint(1000, 9999)}"
            data = {
                "unique_id": u_id,
                "owner_name": st.session_state.username,
                "species": especie,
                "sex": sex,
                "peso": peso,
                "notas": notas
            }
            supabase.table("reptiles").insert(data).execute()
            st.success(f"Ejemplar {u_id} registrado correctamente.")

# --- LÓGICA: PANEL DE CONTROL ---
elif menu == "Panel de Control":
    st.header("📊 Panel de Gestión")
    
    res = supabase.table("reptiles").select("*").eq("owner_name", st.session_state.username).execute()
    reptiles = res.data
    
    if not reptiles:
        st.info("No tienes ejemplares aún. ¡Registra el primero!")
    else:
        # Selección de ejemplar
        options = {r['unique_id']: r for r in reptiles}
        sel_id = st.selectbox("Selecciona un ejemplar para gestionar:", list(options.keys()))
        data_sel = options[sel_id]
        
        # Dashboard superior
        c1, c2, c3 = st.columns(3)
        c1.metric("Especie", data_sel.get('species', '-'))
        c2.metric("Sexo", data_sel.get('sex', '-'))
        c3.metric("Peso", f"{data_sel.get('peso', 0)} g")
        
        st.markdown("---")
        
        # Gráfica simulada de crecimiento
        st.subheader("Tendencia de Crecimiento")
        chart_data = pd.DataFrame({'Día': ['Día 1', 'Día 7', 'Día 14', 'Día 21'], 'Peso (g)': [data_sel.get('peso', 0)-5, data_sel.get('peso', 0)-2, data_sel.get('peso', 0)+2, data_sel.get('peso', 0)+5]})
        st.line_chart(chart_data.set_index('Día'))
        
        with st.expander("Detalles Médicos y Notas"):
            st.write(data_sel.get('notas', 'Sin notas registradas.'))
