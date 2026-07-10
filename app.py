import streamlit as st
import os
from supabase import create_client
import pandas as pd
import random

# --- CONFIGURACIÓN ---
url = st.secrets['PROJECT_URL'].strip().rstrip('/')
key = st.secrets['API_SUPABASE'].strip()
supabase = create_client(url, key)

st.set_page_config(page_title="Herpeto-Logistics Pro", layout="wide", page_icon="🐍")

# --- LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.title("🐍 Acceso Profesional")
    username = st.text_input("Nombre de Propietario")
    if st.button("Ingresar"):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.rerun()
    st.stop()

# --- BARRA LATERAL ---
st.sidebar.title(f"👤 {st.session_state.username}")
menu = st.sidebar.radio("Módulos", ["Panel de Control", "Nuevo Ejemplar", "Alimentación", "Muda", "Veterinario"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# --- LÓGICA DE REGISTRO DE EVENTOS ---
if menu in ["Alimentación", "Muda", "Veterinario"]:
    st.header(f"📝 Registro: {menu}")
    res = supabase.table("reptiles").select("unique_id, name").eq("owner_name", st.session_state.username).execute()
    reptiles = {f"{r['unique_id']} - {r['name']}": r['unique_id'] for r in res.data}
    
    if not reptiles: st.warning("Primero registra un ejemplar.")
    else:
        sel_id = st.selectbox("Ejemplar", list(reptiles.keys()))
        with st.form("event_form"):
            fecha = st.date_input("Fecha")
            if menu == "Alimentación":
                tipo = st.text_input("Alimento"); peso = st.number_input("Peso (g)")
            elif menu == "Muda": comentarios = st.text_area("Notas de Muda")
            else: evaluacion = st.text_area("Evaluación Médica")
            
            if st.form_submit_button("Guardar Registro"):
                data = {"unique_id": reptiles[sel_id], "owner_name": st.session_state.username, "fecha": str(fecha)}
                if menu == "Alimentación": data.update({"tipo_alimento": tipo, "peso_alimento": peso})
                elif menu == "Muda": data.update({"comentarios": comentarios})
                else: data.update({"evaluacion_medica": evaluacion})
                supabase.table(menu.lower()).insert(data).execute()
                st.success(f"Evento de {menu} guardado.")

# --- PANEL DE CONTROL ---
elif menu == "Panel de Control":
    st.header("📊 Dashboard de Gestión")
    res = supabase.table("reptiles").select("*").eq("owner_name", st.session_state.username).execute()
    
    if not res.data: st.info("No hay ejemplares registrados.")
    else:
        opciones = {f"{r['unique_id']} - {r['name']}": r for r in res.data}
        sel = st.selectbox("Selecciona Ejemplar", list(opciones.keys()))
        item = opciones[sel]
        
        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Especie", item.get('species', 'N/A'))
        c2.metric("Sexo", item.get('sex', 'N/A'))
        c3.metric("Peso", f"{item.get('peso', 0)}g")
        
        # Historial con Tabs
        tabs = st.tabs(["Información Legal", "Alimentación", "Muda", "Veterinario"])
        with tabs[0]:
            st.write(f"**Pedimento:** {item.get('pedimento', 'N/A')}")
            st.write(f"**Notas:** {item.get('notas', 'N/A')}")
            
        for i, tabla in enumerate(["alimentacion", "muda", "veterinario"]):
            with tabs[i+1]:
                hist = supabase.table(tabla).select("*").eq("unique_id", item['unique_id']).execute()
                if hist.data: st.table(pd.DataFrame(hist.data))
                else: st.write("Sin registros.")

# --- REGISTRO DE EJEMPLAR ---
elif menu == "Nuevo Ejemplar":
    st.header("➕ Nuevo Ejemplar")
    with st.form("new_reptile"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Nombre"); species = col1.text_input("Especie")
        sex = col1.selectbox("Sexo", ["Macho", "Hembra"])
        pedimento = col2.text_input("Pedimento"); peso = col2.number_input("Peso (g)")
        notas = st.text_area("Notas")
        if st.form_submit_button("Guardar"):
            u_id = f"{species[:2].upper()}-{random.randint(1000, 9999)}"
            data = {"name": name, "species": species, "owner_name": st.session_state.username, "sex": sex, "unique_id": u_id, "pedimento": pedimento, "peso": peso, "notas": notas}
            supabase.table("reptiles").insert(data).execute()
            st.success("Ejemplar registrado.")
