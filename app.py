import streamlit as st
import os
from supabase import create_client
import pandas as pd
import random

# --- CONFIGURACIÓN ---
def get_secret(key):
    return st.secrets[key] if key in st.secrets else os.environ.get(key)

url = get_secret('PROJECT_URL').strip().rstrip('/')
key = get_secret('API_SUPABASE').strip()
supabase = create_client(url, key)

st.set_page_config(page_title="Reptile Logistics Pro", layout="wide", page_icon="🐍")

# --- LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🐍 Reptile Logistics Pro")
    st.markdown("Acceso al sistema de gestión herpetológica.")
    username = st.text_input("Nombre del Propietario")
    if st.button("Entrar al Sistema"):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.rerun()
    st.stop()

# --- BARRA LATERAL ---
st.sidebar.title(f"👤 {st.session_state.username}")
menu = st.sidebar.radio("Módulos de Gestión", ["Panel de Control", "Nuevo Ejemplar"])
st.sidebar.markdown("---")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# --- LÓGICA: PANEL DE CONTROL (VISUAL) ---
if menu == "Panel de Control":
    st.header("📊 Panel de Gestión de Ejemplares")
    
    try:
        response = supabase.table("reptiles").select("*").eq("owner_name", st.session_state.username).execute()
        datos = response.data
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        st.stop()
    
    if not datos:
        st.info("No tienes ejemplares registrados aún.")
    else:
        # Selector de ejemplares
        opciones = {f"{r['unique_id']} - {r.get('name', 'Sin nombre')}" : r for r in datos}
        seleccion = st.selectbox("Selecciona un ejemplar para visualizar:", list(opciones.keys()))
        item = opciones[seleccion]
        
        # Fila de métricas visuales
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Especie", item.get('species', 'N/A'))
        col2.metric("Sexo", item.get('sex', 'N/A'))
        col3.metric("Peso", f"{item.get('peso') or 0} g")
        col4.metric("ID", item.get('unique_id', 'N/A'))
        
        st.markdown("---")
        
        # Layout de visualización
        c_izq, c_der = st.columns([1, 1])
        
        with c_izq:
            st.subheader("📈 Tendencia de Peso")
            peso_val = item.get('peso') or 0
            # Gráfica segura
            df = pd.DataFrame({'Día': ['Registro', 'Actual'], 'Peso (g)': [max(0, peso_val-5), peso_val]})
            st.line_chart(df.set_index('Día'))
            
        with c_der:
            st.subheader("📋 Información Legal y Notas")
            st.write(f"**Nombre:** {item.get('name', 'Sin nombre')}")
            st.write(f"**Pedimento:** {item.get('pedimento', 'No registrado')}")
            st.info(f"**Notas:** {item.get('notas', 'Sin notas adicionales')}")

# --- LÓGICA: REGISTRO ---
elif menu == "Nuevo Ejemplar":
    st.header("➕ Registrar Nuevo Ejemplar")
    with st.form("registro_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nombre del Ejemplar")
            species = st.text_input("Especie")
            sex = st.selectbox("Sexo", ["Macho", "Hembra", "Desconocido"])
        with col2:
            pedimento = st.text_input("Pedimento")
            peso = st.number_input("Peso Inicial (g)", min_value=0, step=1)
        notas = st.text_area("Notas del ejemplar")
        
        if st.form_submit_button("Guardar Registro"):
            u_id = f"{species[:2].upper()}-{random.randint(1000, 9999)}"
            data = {
                "name": name,
                "species": species,
                "owner_name": st.session_state.username,
                "sex": sex,
                "unique_id": u_id,
                "pedimento": pedimento,
                "peso": int(peso),
                "notas": notas
            }
            try:
                supabase.table("reptiles").insert(data).execute()
                st.success(f"Ejemplar {u_id} guardado correctamente.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")
