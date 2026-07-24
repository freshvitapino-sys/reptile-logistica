import streamlit as st
import os
from supabase import create_client
import pandas as pd
import random
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import re
import time

# ============================================================
# CONFIGURACIÓN DE PÁGINA - OPTIMIZADA PARA MÓVIL
# ============================================================
st.set_page_config(
    page_title="RIARE Exotic's",
    page_icon="🦎",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar colapsado por defecto en móvil
)

# ============================================================
# CSS OPTIMIZADO - MOBILE-FIRST CON PATRONES NATIVOS
# ============================================================
st.markdown("""
<style>
    /* ===== RESET Y BASE ===== */
    .stApp { 
        background: linear-gradient(180deg, #0a0e14 0%, #121820 100%);
        padding: 0 !important;
    }

    /* Ocultar header de Streamlit en móvil */
    header[data-testid="stHeader"] { display: none !important; }

    /* ===== TIPOGRAFÍA RESPONSIVA ===== */
    html { font-size: 16px; }
    @media (max-width: 480px) { html { font-size: 15px; } }

    /* ===== CARDS TÁCTILES ===== */
    .reptile-card {
        background: linear-gradient(145deg, #1e2430, #252b3a);
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        border: 1px solid #2a3444;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    .reptile-card:active {
        transform: scale(0.97);
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .reptile-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: #4caf50;
        border-radius: 16px 0 0 16px;
    }
    .reptile-card.selected {
        border-color: #4caf50;
        background: linear-gradient(145deg, #1a2f1e, #1e3a25);
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.2);
    }
    .reptile-card h3 {
        margin: 0 0 0.3rem 0;
        font-size: 1.1rem;
        color: #ffffff !important;
    }
    .reptile-card .meta {
        color: #8b9bb4;
        font-size: 0.85rem;
        margin: 0;
    }
    .reptile-card .badge {
        display: inline-block;
        background: #2a3444;
        color: #4caf50;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        margin-top: 0.5rem;
        font-weight: 600;
    }

    /* ===== BOTTOM NAVIGATION BAR ===== */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(18, 24, 32, 0.95);
        backdrop-filter: blur(20px);
        border-top: 1px solid #2a3444;
        display: flex;
        justify-content: space-around;
        padding: 0.5rem 0;
        z-index: 9999;
        padding-bottom: env(safe-area-inset-bottom, 0.5rem);
    }
    .bottom-nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.3rem 1rem;
        color: #5a6a7a;
        text-decoration: none;
        font-size: 0.7rem;
        transition: color 0.2s;
        border: none;
        background: none;
        cursor: pointer;
    }
    .bottom-nav-item.active {
        color: #4caf50;
    }
    .bottom-nav-item .icon {
        font-size: 1.4rem;
        margin-bottom: 0.2rem;
    }

    /* ===== FLOATING ACTION BUTTON ===== */
    .fab {
        position: fixed;
        bottom: 80px;
        right: 20px;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4caf50, #2e7d32);
        color: white;
        border: none;
        font-size: 1.5rem;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        cursor: pointer;
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .fab:active {
        transform: scale(0.9);
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
    }

    /* ===== TOAST NOTIFICATIONS ===== */
    .toast-container {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10000;
        width: 90%;
        max-width: 400px;
    }
    .toast {
        background: #1e2430;
        border-left: 4px solid #4caf50;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        animation: slideDown 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .toast.error { border-left-color: #f44336; }
    .toast.warning { border-left-color: #ff9800; }
    .toast.info { border-left-color: #2196f3; }
    @keyframes slideDown {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    /* ===== SKELETON LOADING ===== */
    .skeleton {
        background: linear-gradient(90deg, #1e2430 25%, #2a3444 50%, #1e2430 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 8px;
    }
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* ===== STEPPER FORMS ===== */
    .stepper {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5rem;
        padding: 0 1rem;
    }
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
    }
    .step-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #2a3444;
        color: #8b9bb4;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.9rem;
        transition: all 0.3s;
    }
    .step.active .step-circle {
        background: #4caf50;
        color: white;
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.4);
    }
    .step.completed .step-circle {
        background: #2e7d32;
        color: white;
    }
    .step-label {
        font-size: 0.7rem;
        color: #5a6a7a;
        margin-top: 0.3rem;
        white-space: nowrap;
    }
    .step.active .step-label { color: #4caf50; }
    .step-line {
        flex: 1;
        height: 2px;
        background: #2a3444;
        margin: 0 0.5rem;
        margin-bottom: 1.5rem;
        max-width: 60px;
    }
    .step-line.completed { background: #2e7d32; }

    /* ===== SEARCH BAR ===== */
    .search-container {
        position: sticky;
        top: 0;
        background: rgba(10, 14, 20, 0.95);
        backdrop-filter: blur(10px);
        padding: 0.8rem 1rem;
        z-index: 100;
        border-bottom: 1px solid #1e2430;
    }
    .search-input {
        width: 100%;
        background: #1e2430;
        border: 1px solid #2a3444;
        border-radius: 12px;
        padding: 0.8rem 1rem 0.8rem 2.5rem;
        color: #eaeef2;
        font-size: 1rem;
        outline: none;
        transition: border-color 0.2s;
    }
    .search-input:focus {
        border-color: #4caf50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
    }

    /* ===== METRIC CARDS ===== */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.8rem;
        margin-bottom: 1rem;
    }
    @media (min-width: 768px) {
        .metric-grid { grid-template-columns: repeat(4, 1fr); }
    }
    .metric-card {
        background: linear-gradient(145deg, #1e2430, #252b3a);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #2a3444;
    }
    .metric-card .value {
        font-size: 1.4rem;
        font-weight: bold;
        color: #4caf50;
        margin: 0.3rem 0;
    }
    .metric-card .label {
        font-size: 0.75rem;
        color: #8b9bb4;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card.alert { border-color: #f44336; }
    .metric-card.alert .value { color: #f44336; }
    .metric-card.warning { border-color: #ff9800; }
    .metric-card.warning .value { color: #ff9800; }

    /* ===== QUICK STATS BAR ===== */
    .quick-stats {
        display: flex;
        gap: 0.5rem;
        overflow-x: auto;
        padding: 0.5rem 0;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    .quick-stats::-webkit-scrollbar { display: none; }
    .quick-stat-pill {
        background: #1e2430;
        border: 1px solid #2a3444;
        border-radius: 20px;
        padding: 0.4rem 0.8rem;
        white-space: nowrap;
        font-size: 0.8rem;
        color: #8b9bb4;
    }
    .quick-stat-pill strong { color: #4caf50; }

    /* ===== FORM STYLES ===== */
    .stForm {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    .stTextInput > div > div, .stNumberInput > div > div, .stSelectbox > div > div {
        background: #1e2430 !important;
        border: 1px solid #2a3444 !important;
        border-radius: 12px !important;
        color: #eaeef2 !important;
    }
    .stTextInput > div > div:focus-within, .stNumberInput > div > div:focus-within {
        border-color: #4caf50 !important;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #4caf50, #2e7d32) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.9rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    .stButton > button:active {
        transform: scale(0.98) !important;
    }
    .stButton > button.secondary {
        background: #2a3444 !important;
        color: #eaeef2 !important;
    }

    /* ===== TABS OPTIMIZADOS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #121820;
        padding: 0.4rem;
        border-radius: 12px;
        border: 1px solid #1e2430;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #5a6a7a;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        font-size: 0.85rem;
        flex: 1;
        text-align: center;
        border: none;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #1e2430;
        color: #4caf50;
        font-weight: 600;
    }

    /* ===== EXPANDER ===== */
    .stExpander {
        background: #1e2430;
        border-radius: 12px;
        border: 1px solid #2a3444;
        overflow: hidden;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #2a3444; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #4caf50; }

    /* ===== LOGIN SCREEN ===== */
    .login-screen {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 2rem;
        background: linear-gradient(180deg, #0a0e14 0%, #121820 50%, #0d1f0d 100%);
    }
    .login-logo {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .login-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #4caf50;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .login-subtitle {
        color: #5a6a7a;
        margin-bottom: 2rem;
        text-align: center;
    }

    /* ===== CONTENT PADDING FOR BOTTOM NAV ===== */
    .main-content {
        padding-bottom: 80px;
    }

    /* ===== HIDE STREAMLIT ELEMENTS ===== */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none !important; }

    /* ===== DATAFRAME OPTIMIZADA ===== */
    .stDataFrame { 
        background: #1e2430 !important; 
        border-radius: 12px;
        border: 1px solid #2a3444;
    }
    .stDataFrame th { 
        background: #252b3a !important; 
        color: #4caf50 !important;
        font-weight: 600;
    }
    .stDataFrame td { color: #eaeef2 !important; }

    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div {
        background: linear-gradient(90deg, #4caf50, #2e7d32) !important;
    }

    /* ===== ALERTS ===== */
    .stAlert {
        background: #1e2430 !important;
        border: 1px solid #2a3444 !important;
        border-radius: 12px !important;
    }
    .stAlert [data-testid="stAlertContent"] {
        color: #eaeef2 !important;
    }

    /* ===== SECTION HEADERS ===== */
    h1, h2, h3 { color: #ffffff !important; }
    h2 { font-size: 1.3rem !important; margin-top: 1.5rem !important; }
    h3 { font-size: 1.1rem !important; }

    /* ===== DIVIDER ===== */
    hr {
        border-color: #1e2430 !important;
        margin: 1.5rem 0 !important;
    }

    /* ===== PLOTLY CHARTS DARK MODE ===== */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONEXIÓN A SUPABASE CON MANEJO DE ERRORES MEJORADO
# ============================================================
@st.cache_resource(show_spinner=False)
def init_supabase():
    try:
        url = st.secrets['PROJECT_URL'].strip().rstrip('/')
        key = st.secrets['API_SUPABASE'].strip()
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

supabase = init_supabase()

# ============================================================
# FUNCIONES DE UTILIDAD
# ============================================================
def show_toast(message, type_="success", duration=3000):
    """Muestra una notificación tipo toast que desaparece automáticamente."""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    colors = {"success": "#4caf50", "error": "#f44336", "warning": "#ff9800", "info": "#2196f3"}
    icon = icons.get(type_, "ℹ️")

    toast_html = f"""
    <div class="toast-container">
        <div class="toast {type_}">
            <span style="font-size:1.2rem">{icon}</span>
            <span style="color:#eaeef2; font-size:0.9rem">{message}</span>
        </div>
    </div>
    <script>
        setTimeout(() => {{
            const toast = document.querySelector('.toast-container');
            if (toast) toast.style.display = 'none';
        }}, {duration});
    </script>
    """
    st.markdown(toast_html, unsafe_allow_html=True)

def safe_days_between(date_str):
    try:
        if date_str and isinstance(date_str, str) and len(date_str) >= 10:
            d = datetime.strptime(date_str[:10], "%Y-%m-%d")
            return (datetime.now() - d).days
    except:
        pass
    return None

def safe_int(value, default=0):
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

# ============================================================
# CONFIGURACIÓN DE USUARIO
# ============================================================
@st.cache_data(ttl=300)
def obtener_config_usuario(owner_name):
    if not supabase:
        return {"token_voice_monkey": None, "webhook_ha": None}
    try:
        res = supabase.table("usuarios_tokens").select("token_voice_monkey, webhook_ha").eq("owner_name", owner_name).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception as e:
        st.error(f"Error de configuración: {e}")
    return {"token_voice_monkey": None, "webhook_ha": None}

def guardar_config_usuario(owner_name, token_voice_monkey=None, webhook_ha=None):
    if not supabase:
        return False
    data = {"owner_name": owner_name}
    if token_voice_monkey is not None:
        data["token_voice_monkey"] = token_voice_monkey
    if webhook_ha is not None:
        data["webhook_ha"] = webhook_ha
    try:
        supabase.table("usuarios_tokens").upsert(data, on_conflict="owner_name").execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# ============================================================
# NOTIFICACIONES
# ============================================================
def enviar_notificacion_alexa(mensaje, owner_name):
    config = obtener_config_usuario(owner_name)
    token = config.get("token_voice_monkey")
    if not token:
        return False, "Token no configurado"
    try:
        response = requests.post("https://api-v2.voicemonkey.io/announcement", 
                                json={"token": token, "text": mensaje}, timeout=10)
        return response.status_code == 200, "Alexa ✅" if response.status_code == 200 else f"Error {response.status_code}"
    except Exception as e:
        return False, f"Error: {e}"

def enviar_notificacion_ha(mensaje, owner_name, titulo="RIARE"):
    config = obtener_config_usuario(owner_name)
    webhook_url = config.get("webhook_ha")
    if not webhook_url:
        return False, "Webhook no configurado"
    try:
        response = requests.post(webhook_url, json={"message": mensaje, "title": titulo}, timeout=10)
        return response.status_code == 200, "HA ✅" if response.status_code == 200 else f"Error {response.status_code}"
    except Exception as e:
        return False, f"Error: {e}"

# ============================================================
# BASE DE CONOCIMIENTO
# ============================================================
SPECIES_DB = {
    "Boa constrictor": {
        "feed_interval": 10, "temp_range": (26, 32), "humidity": 60,
        "adult_weight": 5000, "shed_interval": 45, "diet": "Roedores",
        "enclosure": "120x60x60 cm", "notes": "Requiere ramas para trepar",
        "birth_weight": 50, "months_to_adult": 36, "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Rata", "Ratón", "Pollo", "Conejo"]
    },
    "Python regius": {
        "feed_interval": 7, "temp_range": (24, 30), "humidity": 55,
        "adult_weight": 2000, "shed_interval": 30, "diet": "Roedores",
        "enclosure": "90x45x45 cm", "notes": "Alta humedad durante muda",
        "birth_weight": 60, "months_to_adult": 24, "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Pinky", "Fuzzy", "Ratón pequeño", "Rata weanling", "Rata pequeña", "Rata mediana", "Rata grande"]
    },
    "Pantherophis guttatus": {
        "feed_interval": 5, "temp_range": (22, 28), "humidity": 40,
        "adult_weight": 800, "shed_interval": 20, "diet": "Roedores",
        "enclosure": "60x40x40 cm", "notes": "Muy activo, necesita espacio",
        "birth_weight": 10, "months_to_adult": 18, "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Ratón", "Pinky", "Fuzzy"]
    },
    "Lampropeltis getula": {
        "feed_interval": 7, "temp_range": (24, 29), "humidity": 50,
        "adult_weight": 1200, "shed_interval": 25, "diet": "Roedores, lagartijas",
        "enclosure": "90x45x45 cm", "notes": "Puede ser caníbal",
        "birth_weight": 15, "months_to_adult": 20, "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Ratón", "Lagartija", "Pinky"]
    },
    "Morelia spilota": {
        "feed_interval": 10, "temp_range": (26, 32), "humidity": 60,
        "adult_weight": 3000, "shed_interval": 40, "diet": "Roedores y aves",
        "enclosure": "120x60x120 cm", "notes": "Arborícola, necesita altura",
        "birth_weight": 40, "months_to_adult": 30, "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Rata", "Ratón", "Pollo", "Codorniz"]
    },
    "Piton Bola": {
        "feed_interval": 7, "temp_range": (24, 30), "humidity": 55,
        "adult_weight": 2000, "shed_interval": 30, "diet": "Roedores",
        "enclosure": "90x45x45 cm", "notes": "Común en cautiverio",
        "birth_weight": 60, "months_to_adult": 24, "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Pinky", "Fuzzy", "Ratón pequeño", "Rata weanling", "Rata pequeña", "Rata mediana", "Rata grande"]
    },
    "Pogona Viticeps": {
        "feed_interval": 1, "temp_range": (35, 40), "humidity": 30,
        "adult_weight": 500, "shed_interval": 14, "diet": "Insectos, verduras",
        "enclosure": "120x60x60 cm + UVB", "notes": "Necesita luz UVB",
        "birth_weight": 5, "months_to_adult": 12, "diet_type": "omnivoro",
        "alimentos_sugeridos": ["Verdura", "Fruta", "Hojas verdes", "Insecto"]
    }
}
DEFAULT_SPECIES = {
    "feed_interval": 7, "temp_range": (25, 30), "humidity": 50,
    "adult_weight": 1000, "shed_interval": 30, "diet": "Roedores",
    "enclosure": "Terrario estándar", "notes": "Sin información",
    "birth_weight": 20, "months_to_adult": 24, "diet_type": "carnivoro",
    "alimentos_sugeridos": None
}

def calcular_recomendacion_presa(peso_serpiente):
    if not peso_serpiente or peso_serpiente <= 0:
        return {"rango_presa": "No disponible", "frecuencia": "Registra peso", "etapa": "Sin datos"}

    if peso_serpiente < 500:
        return {"rango_presa": f"{peso_serpiente*0.10:.0f}g-{peso_serpiente*0.15:.0f}g", 
                "frecuencia": "5-7 días", "etapa": "Juvenil", "porcentaje": "10-15%"}
    elif peso_serpiente < 1000:
        return {"rango_presa": f"{peso_serpiente*0.07:.0f}g-{peso_serpiente*0.10:.0f}g",
                "frecuencia": "7-10 días", "etapa": "Sub-adulto", "porcentaje": "7-10%"}
    else:
        return {"rango_presa": f"{peso_serpiente*0.05:.0f}g-{peso_serpiente*0.07:.0f}g",
                "frecuencia": "10-14 días", "etapa": "Adulto", "porcentaje": "5-7%"}

def get_species_info(species_name, weight=None):
    base = SPECIES_DB.get(species_name, DEFAULT_SPECIES).copy()
    if weight and weight > 0 and species_name in ["Python regius", "Piton Bola"]:
        rec = calcular_recomendacion_presa(weight)
        base.update(rec)
    return base

# ============================================================
# CONSULTAS A SUPABASE
# ============================================================
@st.cache_data(ttl=120)
def get_reptiles(owner):
    if not supabase:
        return []
    try:
        res = supabase.table("reptiles").select("*").eq("owner_name", owner).execute()
        return res.data or []
    except:
        return []

@st.cache_data(ttl=120)
def get_events(table_name, unique_id):
    if not supabase:
        return []
    try:
        res = supabase.table(table_name).select("*").eq("unique_id", unique_id).order("fecha", desc=True).execute()
        return res.data or []
    except:
        return []

@st.cache_data(ttl=120)
def get_peso_history(unique_id):
    if not supabase:
        return []
    try:
        res = supabase.table("peso").select("*").eq("unique_id", unique_id).order("fecha", asc=True).execute()
        return res.data or []
    except:
        return []

# ============================================================
# ESTADO DE SESIÓN
# ============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "selected_reptile" not in st.session_state:
    st.session_state.selected_reptile = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "show_fab_menu" not in st.session_state:
    st.session_state.show_fab_menu = False
if "step" not in st.session_state:
    st.session_state.step = 1

# ============================================================
# LOGIN SCREEN
# ============================================================
if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-screen">
        <div class="login-logo">🦎</div>
        <div class="login-title">RIARE Exotic's</div>
        <div class="login-subtitle">Gestión profesional de reptiles</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        username = st.text_input("👤 Nombre de Propietario", 
                                placeholder="Tu nombre", 
                                label_visibility="collapsed",
                                key="login_user")

        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            if st.button("🚪 Ingresar", use_container_width=True, type="primary"):
                if username.strip():
                    st.session_state.authenticated = True
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.error("Introduce tu nombre")
    st.stop()

# ============================================================
# NAVEGACIÓN INFERIOR (BOTTOM NAV BAR)
# ============================================================
def render_bottom_nav():
    pages = [
        ("dashboard", "🏠", "Inicio"),
        ("reptiles", "🦎", "Mis Reptiles"),
        ("add", "➕", "Agregar"),
        ("stats", "📊", "Estadísticas"),
        ("settings", "⚙️", "Ajustes")
    ]

    nav_html = '<div class="bottom-nav">'
    for page_id, icon, label in pages:
        active = "active" if st.session_state.current_page == page_id else ""
        nav_html += f'<button class="bottom-nav-item {active}" onclick="handleNav('{page_id}')">'
        nav_html += f'<span class="icon">{icon}</span><span>{label}</span></button>'
    nav_html += '</div>'

    # JavaScript para manejar clicks
    nav_html += """
    <script>
    function handleNav(page) {
        const buttons = document.querySelectorAll('.bottom-nav-item');
        buttons.forEach(btn => btn.classList.remove('active'));
        event.currentTarget.classList.add('active');
        // Streamlit no permite JS directo, usamos un workaround con st.query_params
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: page}, '*');
    }
    </script>
    """
    st.markdown(nav_html, unsafe_allow_html=True)

# ============================================================
# HEADER CON BÚSQUEDA
# ============================================================
def render_header(title, show_search=False):
    st.markdown(f'<h2 style="margin-top:0.5rem; margin-bottom:0.5rem; padding:0 1rem;">{title}</h2>', unsafe_allow_html=True)

    if show_search:
        search = st.text_input("🔍 Buscar ejemplar...", 
                              value=st.session_state.search_query,
                              key="search_input",
                              label_visibility="collapsed",
                              placeholder="🔍 Buscar por nombre o especie...")
        st.session_state.search_query = search
        return search
    return ""

# ============================================================
# CARDS DE REPTIL (TÁCTILES Y GRANDES)
# ============================================================
def render_reptile_card(reptile, is_selected=False):
    selected_class = "selected" if is_selected else ""
    name = reptile.get('name', 'Sin nombre')
    species = reptile.get('species', 'N/A')
    sex = reptile.get('sex', 'Desconocido')
    peso = safe_int(reptile.get('peso'))
    fase = reptile.get('fase', '')

    badge = f'<span class="badge">{sex}</span>' if sex != 'Desconocido' else ''
    weight_text = f"{peso}g" if peso > 0 else "Sin peso"

    card_html = f"""
    <div class="reptile-card {selected_class}">
        <h3>🐍 {name}</h3>
        <p class="meta">{species} • {weight_text}</p>
        {badge}
        {f'<span class="badge" style="margin-left:0.3rem">{fase}</span>' if fase else ''}
    </div>
    """
    return card_html

# ============================================================
# STEPPER PARA FORMULARIOS
# ============================================================
def render_stepper(current_step, total_steps, labels):
    html = '<div class="stepper">'
    for i in range(1, total_steps + 1):
        status = "completed" if i < current_step else "active" if i == current_step else ""
        html += f'<div class="step {status}"><div class="step-circle">{i}</div><span class="step-label">{labels[i-1]}</span></div>'
        if i < total_steps:
            line_status = "completed" if i < current_step else ""
            html += f'<div class="step-line {line_status}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ============================================================
# METRICS GRID
# ============================================================
def render_metric_grid(metrics):
    """metrics: lista de dicts con 'label', 'value', 'status' (opt)"""
    html = '<div class="metric-grid">'
    for m in metrics:
        status = m.get('status', '')
        html += f"""
        <div class="metric-card {status}">
            <div class="label">{m['label']}</div>
            <div class="value">{m['value']}</div>
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ============================================================
# CONTENIDO PRINCIPAL
# ============================================================
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ---- PÁGINA: DASHBOARD ----
if st.session_state.current_page == "dashboard":
    render_header("📊 Panel de Control")

    reptiles = get_reptiles(st.session_state.username)

    if not reptiles:
        st.info("🦎 No tienes ejemplares registrados. Toca ➕ para agregar uno.")
    else:
        # Quick stats scrollable
        total = len(reptiles)
        species_count = len(set(r.get('species', '') for r in reptiles))

        st.markdown(f"""
        <div class="quick-stats">
            <div class="quick-stat-pill">🦎 <strong>{total}</strong> ejemplares</div>
            <div class="quick-stat-pill">🔬 <strong>{species_count}</strong> especies</div>
            <div class="quick-stat-pill">👤 {st.session_state.username}</div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("🦎 Últimos ejemplares")

        # Mostrar cards de reptiles (máximo 4 en dashboard)
        for reptile in reptiles[:4]:
            is_selected = st.session_state.selected_reptile == reptile['unique_id']
            st.markdown(render_reptile_card(reptile, is_selected), unsafe_allow_html=True)

            # Botón invisible encima del card para capturar click
            if st.button(f"Ver {reptile.get('name', 'Reptil')}", 
                        key=f"dash_btn_{reptile['unique_id']}",
                        use_container_width=True):
                st.session_state.selected_reptile = reptile['unique_id']
                st.session_state.current_page = "reptiles"
                st.rerun()

        if len(reptiles) > 4:
            if st.button("Ver todos mis reptiles →", use_container_width=True):
                st.session_state.current_page = "reptiles"
                st.rerun()

        # Alertas rápidas
        st.subheader("🔔 Alertas")
        alertas = []
        for r in reptiles:
            alim = get_events("alimentacion", r['unique_id'])
            if alim and len(alim) > 0:
                dias = safe_days_between(alim[0].get('fecha'))
                if dias and dias > 10:
                    alertas.append(f"⚠️ **{r.get('name')}** lleva {dias} días sin comer")

        if alertas:
            for alerta in alertas[:3]:
                st.warning(alerta)
        else:
            st.success("✅ Todo en orden. Sin alertas pendientes.")

# ---- PÁGINA: MIS REPTILES ----
elif st.session_state.current_page == "reptiles":
    search = render_header("🦎 Mis Reptiles", show_search=True)

    reptiles = get_reptiles(st.session_state.username)

    if not reptiles:
        st.info("No hay ejemplares. Toca ➕ para agregar uno.")
    else:
        # Filtrar por búsqueda
        filtered = [r for r in reptiles if search.lower() in r.get('name','').lower() 
                    or search.lower() in r.get('species','').lower()] if search else reptiles

        if not filtered:
            st.info("🔍 No se encontraron resultados")
        else:
            for reptile in filtered:
                is_selected = st.session_state.selected_reptile == reptile['unique_id']
                st.markdown(render_reptile_card(reptile, is_selected), unsafe_allow_html=True)

                if st.button(f"Seleccionar {reptile.get('name', 'Reptil')}", 
                            key=f"rept_btn_{reptile['unique_id']}",
                            use_container_width=True):
                    st.session_state.selected_reptile = reptile['unique_id']
                    st.rerun()

            # Si hay seleccionado, mostrar detalle
            if st.session_state.selected_reptile:
                selected = next((r for r in reptiles if r['unique_id'] == st.session_state.selected_reptile), None)
                if selected:
                    st.divider()
                    st.subheader(f"📋 {selected.get('name', 'Reptil')}")

                    # Métricas
                    species_info = get_species_info(selected.get('species', ''), safe_int(selected.get('peso')))
                    alim = get_events("alimentacion", selected['unique_id'])
                    muda = get_events("muda", selected['unique_id'])
                    peso_hist = get_peso_history(selected['unique_id'])

                    dias_alim = safe_days_between(alim[0].get('fecha')) if alim else None
                    dias_muda = safe_days_between(muda[0].get('fecha')) if muda else None

                    metrics = [
                        {"label": "Peso", "value": f"{safe_int(selected.get('peso'))}g"},
                        {"label": "Alimentación", "value": f"Hace {dias_alim}d" if dias_alim is not None else "Sin datos", 
                         "status": "warning" if dias_alim and dias_alim > 10 else ""},
                        {"label": "Muda", "value": f"Hace {dias_muda}d" if dias_muda is not None else "Sin datos"},
                        {"label": "Especie", "value": selected.get('species', 'N/A')[:10]}
                    ]
                    render_metric_grid(metrics)

                    # Tabs de detalle
                    tabs = st.tabs(["🍽️ Alim", "🔄 Muda", "⚖️ Peso", "🏥 Vet"])

                    with tabs[0]:
                        if alim:
                            df = pd.DataFrame(alim[:5])
                            df['días'] = df['fecha'].apply(lambda x: safe_days_between(x))
                            st.dataframe(df[['fecha', 'tipo_alimento', 'días']], use_container_width=True, hide_index=True)
                        else:
                            st.info("Sin registros")

                    with tabs[1]:
                        if muda:
                            df = pd.DataFrame(muda[:5])
                            df['días'] = df['fecha'].apply(lambda x: safe_days_between(x))
                            st.dataframe(df[['fecha', 'comentarios', 'días']], use_container_width=True, hide_index=True)
                        else:
                            st.info("Sin registros")

                    with tabs[2]:
                        if peso_hist and len(peso_hist) > 1:
                            df = pd.DataFrame(peso_hist)
                            df['fecha'] = pd.to_datetime(df['fecha'])
                            fig = px.line(df, x='fecha', y='peso', 
                                        title='Evolución de peso',
                                        template='plotly_dark')
                            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20),
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            plot_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        else:
                            st.info("Registra pesos para ver evolución")

                    with tabs[3]:
                        vet = get_events("veterinario", selected['unique_id'])
                        if vet:
                            df = pd.DataFrame(vet[:5])
                            st.dataframe(df[['fecha', 'evaluacion_medica']], use_container_width=True, hide_index=True)
                        else:
                            st.info("Sin registros")

                    # Acciones rápidas
                    st.subheader("⚡ Acciones rápidas")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🍽️ Alimentar", use_container_width=True):
                            st.session_state.current_page = "add"
                            st.session_state.add_type = "alimentacion"
                            st.rerun()
                    with col2:
                        if st.button("⚖️ Pesar", use_container_width=True):
                            st.session_state.current_page = "add"
                            st.session_state.add_type = "peso"
                            st.rerun()
                    with col3:
                        if st.button("🔄 Muda", use_container_width=True):
                            st.session_state.current_page = "add"
                            st.session_state.add_type = "muda"
                            st.rerun()

# ---- PÁGINA: AGREGAR (CON STEPPER) ----
elif st.session_state.current_page == "add":
    add_type = st.session_state.get("add_type", "reptil")

    if add_type == "reptil":
        render_header("➕ Nuevo Ejemplar")
        render_stepper(st.session_state.step, 3, ["Datos", "Detalles", "Confirmar"])

        with st.form("new_reptile_step"):
            if st.session_state.step == 1:
                name = st.text_input("📛 Nombre *", placeholder="Ej: Medusa")
                species = st.selectbox("🔬 Especie *", list(SPECIES_DB.keys()) + ["Otra"])
                if species == "Otra":
                    species = st.text_input("Especifica la especie")
                sex = st.selectbox("⚥ Sexo", ["Macho", "Hembra", "Desconocido"])

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Siguiente →", use_container_width=True):
                        if name and species:
                            st.session_state.temp_reptile = {"name": name, "species": species, "sex": sex}
                            st.session_state.step = 2
                            st.rerun()
                        else:
                            st.error("Nombre y especie son obligatorios")
                with col2:
                    if st.form_submit_button("Cancelar", use_container_width=True, type="secondary"):
                        st.session_state.step = 1
                        st.session_state.current_page = "dashboard"
                        st.rerun()

            elif st.session_state.step == 2:
                temp = st.session_state.get("temp_reptile", {})
                fase = st.text_input("🧬 Fase / Gen (opcional)", placeholder="Ej: Albino, Pastel")
                pedimento = st.text_input("📄 Pedimento (opcional)")
                peso = st.number_input("⚖️ Peso inicial (g)", min_value=0, step=50)
                notas = st.text_area("📝 Notas")

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("← Anterior", use_container_width=True):
                        st.session_state.step = 1
                        st.rerun()
                with col2:
                    if st.form_submit_button("Siguiente →", use_container_width=True):
                        temp.update({"fase": fase, "pedimento": pedimento, "peso": int(peso), "notas": notas})
                        st.session_state.temp_reptile = temp
                        st.session_state.step = 3
                        st.rerun()

            elif st.session_state.step == 3:
                temp = st.session_state.get("temp_reptile", {})
                st.write("**Resumen:**")
                st.write(f"📛 Nombre: {temp.get('name')}")
                st.write(f"🔬 Especie: {temp.get('species')}")
                st.write(f"⚥ Sexo: {temp.get('sex')}")
                st.write(f"⚖️ Peso: {temp.get('peso', 0)}g")

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("← Anterior", use_container_width=True):
                        st.session_state.step = 2
                        st.rerun()
                with col2:
                    if st.form_submit_button("💾 Guardar", use_container_width=True):
                        u_id = f"{temp['species'][:2].upper()}{random.randint(1000,9999)}"
                        data = {
                            "name": temp.get('name'),
                            "species": temp.get('species'),
                            "owner_name": st.session_state.username,
                            "sex": temp.get('sex'),
                            "unique_id": u_id,
                            "pedimento": temp.get('pedimento', ''),
                            "peso": temp.get('peso', 0),
                            "notas": temp.get('notas', ''),
                            "fase": temp.get('fase', '')
                        }
                        try:
                            supabase.table("reptiles").insert(data).execute()
                            st.session_state.step = 1
                            st.session_state.temp_reptile = {}
                            st.session_state.selected_reptile = u_id
                            st.session_state.current_page = "reptiles"
                            st.cache_data.clear()
                            st.success(f"✅ {temp.get('name')} registrado!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    elif add_type == "alimentacion":
        render_header("🍽️ Alimentación")
        reptiles = get_reptiles(st.session_state.username)

        if not reptiles:
            st.warning("Primero registra un ejemplar")
        else:
            # Selector de reptil con cards
            st.subheader("Selecciona un ejemplar")
            for r in reptiles[:5]:
                if st.button(f"{r.get('name')} ({r.get('species')})", 
                           key=f"feed_sel_{r['unique_id']}", use_container_width=True):
                    st.session_state.feed_reptile = r['unique_id']
                    st.rerun()

            feed_id = st.session_state.get("feed_reptile")
            if feed_id:
                reptile = next((r for r in reptiles if r['unique_id'] == feed_id), None)
                if reptile:
                    species_info = get_species_info(reptile.get('species'))
                    alimentos = species_info.get('alimentos_sugeridos', ["Otro"])

                    with st.form("feed_form"):
                        st.markdown(f"**Registrando alimentación para: {reptile.get('name')}**")
                        fecha = st.date_input("📅 Fecha", value=datetime.now())
                        tipo = st.selectbox("🍗 Alimento", alimentos)
                        peso_alim = st.number_input("⚖️ Peso (g)", min_value=0, step=5)
                        notas = st.text_area("📝 Notas")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Cancelar", use_container_width=True):
                                st.session_state.feed_reptile = None
                                st.rerun()
                        with col2:
                            if st.form_submit_button("💾 Guardar", use_container_width=True):
                                data = {
                                    "unique_id": feed_id,
                                    "owner_name": st.session_state.username,
                                    "fecha": str(fecha),
                                    "tipo_alimento": tipo,
                                    "peso_alimento": int(peso_alim)
                                }
                                try:
                                    supabase.table("alimentacion").insert(data).execute()
                                    st.session_state.feed_reptile = None
                                    st.cache_data.clear()
                                    st.success("✅ Registrado!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

    elif add_type == "peso":
        render_header("⚖️ Registro de Peso")
        reptiles = get_reptiles(st.session_state.username)

        if not reptiles:
            st.warning("Primero registra un ejemplar")
        else:
            st.subheader("Selecciona un ejemplar")
            for r in reptiles[:5]:
                current = safe_int(r.get('peso'))
                if st.button(f"{r.get('name')} (Actual: {current}g)", 
                           key=f"weight_sel_{r['unique_id']}", use_container_width=True):
                    st.session_state.weight_reptile = r['unique_id']
                    st.rerun()

            weight_id = st.session_state.get("weight_reptile")
            if weight_id:
                reptile = next((r for r in reptiles if r['unique_id'] == weight_id), None)
                if reptile:
                    current = safe_int(reptile.get('peso'))
                    with st.form("weight_form"):
                        st.markdown(f"**{reptile.get('name')}** - Peso actual: {current}g")
                        fecha = st.date_input("📅 Fecha", value=datetime.now())
                        nuevo = st.number_input("⚖️ Nuevo peso (g)", min_value=0, step=10, value=current)
                        notas = st.text_area("📝 Notas")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Cancelar", use_container_width=True):
                                st.session_state.weight_reptile = None
                                st.rerun()
                        with col2:
                            if st.form_submit_button("💾 Guardar", use_container_width=True):
                                try:
                                    supabase.table("peso").insert({
                                        "unique_id": weight_id,
                                        "owner_name": st.session_state.username,
                                        "fecha": str(fecha),
                                        "peso": int(nuevo),
                                        "notas": notas
                                    }).execute()
                                    supabase.table("reptiles").update({"peso": int(nuevo)}).eq("unique_id", weight_id).execute()
                                    st.session_state.weight_reptile = None
                                    st.cache_data.clear()
                                    st.success("✅ Peso actualizado!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

    elif add_type == "muda":
        render_header("🔄 Registrar Muda")
        reptiles = get_reptiles(st.session_state.username)

        if not reptiles:
            st.warning("Primero registra un ejemplar")
        else:
            st.subheader("Selecciona un ejemplar")
            for r in reptiles[:5]:
                if st.button(f"{r.get('name')} ({r.get('species')})", 
                           key=f"shed_sel_{r['unique_id']}", use_container_width=True):
                    st.session_state.shed_reptile = r['unique_id']
                    st.rerun()

            shed_id = st.session_state.get("shed_reptile")
            if shed_id:
                reptile = next((r for r in reptiles if r['unique_id'] == shed_id), None)
                if reptile:
                    with st.form("shed_form"):
                        st.markdown(f"**{reptile.get('name')}**")
                        fecha = st.date_input("📅 Fecha", value=datetime.now())
                        comentarios = st.text_area("📝 Observaciones")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Cancelar", use_container_width=True):
                                st.session_state.shed_reptile = None
                                st.rerun()
                        with col2:
                            if st.form_submit_button("💾 Guardar", use_container_width=True):
                                try:
                                    supabase.table("muda").insert({
                                        "unique_id": shed_id,
                                        "owner_name": st.session_state.username,
                                        "fecha": str(fecha),
                                        "comentarios": comentarios
                                    }).execute()
                                    st.session_state.shed_reptile = None
                                    st.cache_data.clear()
                                    st.success("✅ Muda registrada!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

    else:
        # Menú de selección de tipo
        render_header("➕ ¿Qué deseas registrar?")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🦎 Nuevo Reptil", use_container_width=True):
                st.session_state.add_type = "reptil"
                st.rerun()
            if st.button("🍽️ Alimentación", use_container_width=True):
                st.session_state.add_type = "alimentacion"
                st.rerun()
        with col2:
            if st.button("⚖️ Peso", use_container_width=True):
                st.session_state.add_type = "peso"
                st.rerun()
            if st.button("🔄 Muda", use_container_width=True):
                st.session_state.add_type = "muda"
                st.rerun()
        if st.button("🏥 Veterinario", use_container_width=True):
            st.session_state.add_type = "veterinario"
            st.rerun()

# ---- PÁGINA: ESTADÍSTICAS ----
elif st.session_state.current_page == "stats":
    render_header("📊 Estadísticas")
    reptiles = get_reptiles(st.session_state.username)

    if not reptiles:
        st.info("No hay datos para mostrar")
    else:
        total = len(reptiles)
        st.metric("Total de ejemplares", total)

        # Gráfico de especies
        df_species = pd.DataFrame(reptiles)
        if 'species' in df_species.columns:
            counts = df_species['species'].value_counts().reset_index()
            counts.columns = ['Especie', 'Cantidad']
            fig = px.bar(counts, x='Especie', y='Cantidad', 
                        color='Cantidad', color_continuous_scale='Greens',
                        template='plotly_dark')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Gráfico de sexo
        if 'sex' in df_species.columns:
            sex_counts = df_species['sex'].value_counts().reset_index()
            sex_counts.columns = ['Sexo', 'Cantidad']
            fig2 = px.pie(sex_counts, names='Sexo', values='Cantidad', 
                         hole=0.4, template='plotly_dark')
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', 
                             margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

# ---- PÁGINA: AJUSTES ----
elif st.session_state.current_page == "settings":
    render_header("⚙️ Configuración")

    # Tabs para organizar
    tab1, tab2, tab3 = st.tabs(["🔊 Notificaciones", "👤 Cuenta", "ℹ️ Info"])

    with tab1:
        config = obtener_config_usuario(st.session_state.username)

        st.subheader("🔊 Alexa (Voice Monkey)")
        if config.get("token_voice_monkey"):
            st.success("✅ Configurado")
            if st.button("🗑️ Eliminar token"):
                if st.checkbox("¿Confirmar eliminación?"):
                    guardar_config_usuario(st.session_state.username, token_voice_monkey=None)
                    st.rerun()
        else:
            st.info("No configurado")

        with st.form("token_form"):
            token = st.text_input("Token de Voice Monkey", type="password")
            if st.form_submit_button("💾 Guardar"):
                if token:
                    guardar_config_usuario(st.session_state.username, token_voice_monkey=token)
                    st.success("Token guardado")
                    st.rerun()

        st.subheader("🏠 Home Assistant")
        if config.get("webhook_ha"):
            st.success("✅ Configurado")
        else:
            st.info("No configurado")

        with st.form("webhook_form"):
            webhook = st.text_input("URL del Webhook")
            if st.form_submit_button("💾 Guardar"):
                if webhook:
                    guardar_config_usuario(st.session_state.username, webhook_ha=webhook)
                    st.success("Webhook guardado")
                    st.rerun()

        # Test
        st.subheader("🧪 Probar notificaciones")
        if st.button("Enviar prueba", use_container_width=True):
            msg = "Prueba desde RIARE Exotic's"
            r1 = enviar_notificacion_alexa(msg, st.session_state.username)
            r2 = enviar_notificacion_ha(msg, st.session_state.username)
            st.write(f"Alexa: {r1[1]}")
            st.write(f"HA: {r2[1]}")

    with tab2:
        st.write(f"**Usuario:** {st.session_state.username}")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.selected_reptile = None
            st.rerun()

    with tab3:
        st.markdown("""
        **RIARE Exotic's v4.0**

        Sistema de gestión herpetológica optimizado para móvil.

        Funciones:
        • Registro de reptiles con pasos guiados
        • Control de alimentación, peso y muda
        • Notificaciones a Alexa y Home Assistant
        • Estadísticas visuales
        • Interfaz adaptativa
        """)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# BOTTOM NAVIGATION (RENDER AL FINAL PARA QUE ESTÉ ARRIBA EN Z-INDEX)
# ============================================================
# Usamos botones de Streamlit en lugar de HTML puro para que funcionen
st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

cols = st.columns(5)
pages = [
    ("dashboard", "🏠", "Inicio"),
    ("reptiles", "🦎", "Reptiles"),
    ("add", "➕", "Agregar"),
    ("stats", "📊", "Stats"),
    ("settings", "⚙️", "Ajustes")
]

for i, (page_id, icon, label) in enumerate(pages):
    with cols[i]:
        active_style = "primary" if st.session_state.current_page == page_id else "secondary"
        if st.button(f"{icon}", key=f"nav_{page_id}", use_container_width=True, type=active_style):
            st.session_state.current_page = page_id
            if page_id == "add":
                st.session_state.add_type = "menu"
                st.session_state.step = 1
            st.rerun()
        st.caption(label, unsafe_allow_html=True)
