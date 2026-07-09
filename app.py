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
    st.error("❌ Error conectando a la base de datos. Revisa tus Secrets.")
    st.stop()

st.set_page_config(page_title="Reptile Logistics", layout="wide")

# --- LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🐍 Acceso al Sistema")
    username = st.text_input("Nombre del Propietario")
    if st.button("Ingresar"):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.rerun()
    st.stop()

# --- MENÚ ---
menu = st.sidebar.radio("Navegación", ["Panel de Control", "Nuevo Ejemplar"])
st.sidebar.markdown(f"---")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# --- REGISTRO ---
if menu == "Nuevo Ejemplar":
    st.header("➕ Registrar Nuevo Ejemplar")
    with st.form("registro_form"):
        col1, col2 = st.columns(2)
        with col1:
            especie = st.text_input("Especie")
            sexo = st.selectbox("Sexo", ["Macho", "Hembra", "Desconocido"])
        with col2:
            peso = st.number_input("Peso Inicial (g)", min_value=0.0)
            fecha_nacimiento = st.date_input("Fecha de Nacimiento / Adquisición")
        
        notas = st.text_area("Notas / Historial Médico")
        
        if st.form_submit_button("Registrar"):
            # Generación automática de ID: Especie + num random
            u_id = f"{especie[:2].upper()}-{random.randint(1000, 9999)}"
            data = {
                "unique_id": u_id,
                "owner_name": st.session_state.username,
                "species": especie,
                "sexo": sexo,
                "peso": peso,
                "notas": notas
            }
            supabase.table("reptiles").insert(data).execute()
            st.success(f"Ejemplar {u_id} registrado exitosamente.")

# --- PANEL DE CONTROL (Copia esta parte en tu app.py) ---
        elif menu == "Panel de Control":
            st.header(f"📦 Ejemplares de: {st.session_state.username}")
            
            res = supabase.table("reptiles").select("*").eq("owner_name", st.session_state.username).execute()
            reptiles = res.data
            
            if not reptiles:
                st.info("No tienes ejemplares registrados aún.")
            else:
                options = {r['unique_id']: r for r in reptiles}
                sel_id = st.selectbox("Selecciona un ejemplar:", list(options.keys()))
                data_sel = options[sel_id]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Especie", data_sel.get('species', 'N/A'))
                c2.metric("Sexo", data_sel.get('sex', 'N/A'))  # Aquí estaba el error
                c3.metric("Peso", f"{data_sel.get('peso', 0)} g")
                
                st.subheader("📊 Historial de Crecimiento")
                # Simulación de datos para la gráfica
                historial = pd.DataFrame({'Día': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie'], 
                                         'Peso (g)': [data_sel.get('peso', 0)-10, data_sel.get('peso', 0)-5, data_sel.get('peso', 0), data_sel.get('peso', 0)+2, data_sel.get('peso', 0)+5]})
                st.line_chart(historial.set_index('Día'))
                
                with st.expander("Ver notas del ejemplar"):
                    st.write(data_sel.get('notas', 'Sin notas adicionales.'))
