import streamlit as st
import os
from supabase import create_client
from groq import Groq
from datetime import datetime

# --- CONFIGURACIÓN DE SECRETOS ---
def get_secret(key):
    return st.secrets[key] if key in st.secrets else os.environ.get(key)

# Inicialización segura
try:
    url = get_secret('PROJECT_URL').strip().rstrip('/')
    key = get_secret('API_SUPABASE').strip()
    supabase = create_client(url, key)
    client = Groq(api_key=get_secret('GROQ_API_KEY'))
except Exception:
    st.error("⚠️ Error de configuración. Revisa tus Secrets.")
    st.stop()

# --- INTERFAZ Y ESTILO ---
st.set_page_config(page_title="Reptile Logistics Pro", layout="wide")

# --- LÓGICA DE LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Acceso al Sistema")
    with st.form("login_form"):
        username = st.text_input("Nombre del Propietario / Dueño")
        submit = st.form_submit_button("Entrar al Dashboard")
        if submit and username:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
    st.stop()

# --- DASHBOARD PRINCIPAL ---
st.sidebar.title(f"👤 {st.session_state.username}")
menu = st.sidebar.radio("Navegación", ["Panel de Control", "Registrar Nuevo Ejemplar", "Cerrar Sesión"])

if menu == "Cerrar Sesión":
    st.session_state.authenticated = False
    st.rerun()

# --- SECCIÓN: REGISTRAR NUEVO ---
if menu == "Registrar Nuevo Ejemplar":
    st.header("➕ Registro de Nuevo Ejemplar")
    with st.form("new_reptile_form"):
        u_id = st.text_input("ID Único (ej: PB0003)")
        species = st.text_input("Especie")
        notes = st.text_area("Notas iniciales")
        if st.form_submit_button("Confirmar Registro"):
            data = {"unique_id": u_id, "owner": st.session_state.username, "species": species}
            supabase.table("reptiles").insert(data).execute()
            st.success(f"¡{u_id} registrado con éxito!")

# --- SECCIÓN: PANEL DE CONTROL (Visualización) ---
elif menu == "Panel de Control":
    st.header("🐍 Gestión de Inventario Activo")
    
    # Filtrar reptiles por el dueño logueado
    res = supabase.table("reptiles").select("*").eq("owner", st.session_state.username).execute()
    reptiles = res.data
    
    if not reptiles:
        st.info("No tienes ejemplares registrados aún. Ve a 'Registrar Nuevo Ejemplar'.")
    else:
        options = {r['unique_id']: r['id'] for r in reptiles}
        selected_id = st.sidebar.selectbox("Selecciona un ejemplar", list(options.keys()))
        reptil_id = options[selected_id]

        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader(f"Métricas: {selected_id}")
            peso = st.number_input("Nuevo peso (g)", min_value=0.0)
            if st.button("Guardar Peso"):
                supabase.table("events").insert({"reptile_id": reptil_id, "event_type": "peso", "value_numeric": peso}).execute()
                st.toast("✅ Peso actualizado")

        with col2:
            st.subheader("Análisis de Salud IA")
            if st.button("Consultar Llama 3"):
                with st.spinner("Analizando tendencias..."):
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"El reptil {selected_id} de {st.session_state.username} registró {peso}g. ¿Alguna recomendación?"}],
                        model="llama-3.3-70b-versatile",
                    )
                    st.info(chat.choices[0].message.content)
