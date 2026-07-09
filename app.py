import streamlit as st
import os
from supabase import create_client
from groq import Groq
from datetime import datetime, timezone

# Configuración desde los "Secrets" de Streamlit Cloud
url = os.environ.get('PROJECT_URL').strip().rstrip('/')
key = os.environ.get('API_SUPABASE').strip()
supabase = create_client(url, key)
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

st.set_page_config(page_title="Reptile Logística", layout="centered")
st.title("🐍 Reptile Logística")

# Selección de Reptil
reptiles = supabase.table("reptiles").select("id, unique_id").execute().data
options = {r['unique_id']: r['id'] for r in reptiles}
selected_id = st.sidebar.selectbox("Selecciona un ejemplar", list(options.keys()))
reptil_id = options[selected_id]

# Acciones
col1, col2 = st.columns(2)
with col1:
    peso = st.number_input("Nuevo peso (g)", min_value=0.0)
    if st.button("Registrar Peso"):
        supabase.table("events").insert({"reptile_id": reptil_id, "event_type": "peso", "value_numeric": peso}).execute()
        st.success("Peso guardado")

with col2:
    if st.button("Registrar Muda"):
        supabase.table("events").insert({"reptile_id": reptil_id, "event_type": "muda", "value_numeric": 0}).execute()
        st.success("Muda registrada")

# Análisis IA
if st.button("Obtener Diagnóstico IA"):
    with st.spinner("Analizando..."):
        prompt = f"El reptil {selected_id} pesa {peso}g. Dame un consejo breve de salud."
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        st.write(chat.choices[0].message.content)