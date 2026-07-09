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

# --- LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🐍 Reptile Logistics Pro")
    username = st.text_input("Nombre del Propietario")
    if st.button("Entrar"):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.rerun()
    st.stop()

# --- MENÚ DE BARRA LATERAL ---
st.sidebar.title(f"👤 {st.session_state.username}")
menu = st.sidebar.radio("Módulos de Gestión", 
                       ["Panel de Control", "Nuevo Ejemplar", "Alimentación", "Reproducción", "Muda"])

st.sidebar.markdown("---")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# --- LÓGICA DE NAVEGACIÓN ---

# MÓDULO: REGISTRO
if menu == "Nuevo Ejemplar":
    st.header("➕ Registro de Nuevo Ejemplar")
    # (Formulario de registro igual al anterior...)

# MÓDULO: PANEL DE CONTROL
elif menu == "Panel de Control":
    st.header("📊 Panel de Gestión")
    # (Tu lógica de selección de ejemplar y métricas...)

# MÓDULOS DE EVENTOS (Estructura dinámica)
elif menu in ["Alimentación", "Reproducción", "Muda"]:
    st.header(f"📝 Registro de: {menu}")
    
    # Obtener lista de ejemplares para seleccionar
    res = supabase.table("reptiles").select("unique_id").eq("owner_name", st.session_state.username).execute()
    reptiles = [r['unique_id'] for r in res.data]
    
    if not reptiles:
        st.warning("No tienes ejemplares para registrar eventos.")
    else:
        sel_id = st.selectbox("Selecciona un ejemplar:", reptiles)
        
        with st.form(f"form_{menu}"):
            st.write(f"Agregar nuevo registro de **{menu}** para {sel_id}")
            fecha = st.date_input("Fecha")
            detalles = st.text_area("Detalles / Notas del evento")
            
            if st.form_submit_button("Guardar Registro"):
                data = {
                    "unique_id": sel_id,
                    "event_type": menu,
                    "fecha": str(fecha),
                    "detalles": detalles,
                    "owner_name": st.session_state.username
                }
                # Aquí deberías tener una tabla llamada 'eventos' en Supabase
                try:
                    supabase.table("eventos").insert(data).execute()
                    st.success(f"Registro de {menu} guardado.")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
