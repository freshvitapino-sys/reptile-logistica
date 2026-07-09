import streamlit as st
import os
from supabase import create_client
import pandas as pd
import random

# --- CONFIGURACIÓN ---
def get_secret(key):
    return st.secrets[key] if key in st.secrets else os.environ.get(key)

try:
    url = get_secret('PROJECT_URL').strip().rstrip('/')
    key = get_secret('API_SUPABASE').strip()
    supabase = create_client(url, key)
except Exception:
    st.error("Error de configuración en Secrets.")
    st.stop()

st.set_page_config(page_title="Reptile Logistics", layout="wide", page_icon="🐍")

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

# --- NAVEGACIÓN ---
menu = st.sidebar.radio("Navegación", ["Panel de Control", "Nuevo Ejemplar"])
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# --- REGISTRO ---
if menu == "Nuevo Ejemplar":
    st.header("➕ Registro de Nuevo Ejemplar")
    with st.form("registro"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nombre del Ejemplar")
            species = st.text_input("Especie")
            sex = st.selectbox("Sexo", ["Macho", "Hembra", "Desconocido"])
        with col2:
            pedimento = st.text_input("Pedimento")
            peso = st.number_input("Peso (g)", min_value=0, step=1)
        notas = st.text_area("Notas")
        
        if st.form_submit_button("Guardar"):
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
                st.success("Ejemplar registrado.")
            except Exception as e:
                st.error(f"Error: {e}")

# --- PANEL DE CONTROL ---
elif menu == "Panel de Control":
    st.header("📊 Panel de Gestión")
    res = supabase.table("reptiles").select("*").eq("owner_name", st.session_state.username).execute()
    
    if not res.data:
        st.info("Sin registros.")
    else:
        reptiles = res.data
        options = {r['unique_id']: r for r in reptiles}
        sel_id = st.selectbox("Selecciona:", list(options.keys()))
        item = options[sel_id]
        
        # Manejo de valores vacíos
        p_val = item.get('peso') if item.get('peso') is not None else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Especie", item.get('species', '-'))
        c2.metric("Sexo", item.get('sex', '-'))
        c3.metric("Peso", f"{p_val} g")
        
        st.write(f"**Pedimento:** {item.get('pedimento', 'N/A')}")
        st.write(f"**Notas:** {item.get('notas', 'N/A')}")
        
        # Gráfica segura
        df = pd.DataFrame({'Estado': ['Peso Inicial', 'Actual'], 'g': [max(0, p_val-10), p_val]})
        st.line_chart(df.set_index('Estado'))
