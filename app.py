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

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(
    page_title="RIARE Exotic's",
    page_icon="🦎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- ESTILOS CSS (TEMA OSCURO + MOVIL) ----------
st.markdown("""
<style>
    .stApp { background-color: #0e1117; padding: 0.5rem; }
    .css-1d391kg, .stSidebar { background-color: #1e2229; }
    .stAlert, .stForm, .stSelectbox, .stTextInput, .stNumberInput, .stDataFrame, .stMarkdown {
        background-color: #262b33;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        color: #eaeef2;
        font-size: 1rem;
    }
    div[data-testid="metric-container"] {
        background-color: #1e2229;
        border-radius: 12px;
        padding: 1rem;
        border-left: 5px solid #4caf50;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    div[data-testid="metric-container"] label { color: #b0bec5 !important; font-size: 0.9rem !important; }
    div[data-testid="metric-container"] div { color: #ffffff !important; font-size: 1.4rem !important; }
    .stButton > button {
        background-color: #4caf50;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: 0.3s;
        width: 100%;
        min-height: 50px;
    }
    .stButton > button:hover { background-color: #388e3c; color: white; }
    .ejemplar-btn {
        background-color: #2a2f39;
        color: #eaeef2;
        border: 2px solid #3a4050;
        border-radius: 12px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        font-weight: bold;
        text-align: center;
        transition: 0.3s;
        cursor: pointer;
        font-size: 0.95rem;
    }
    .ejemplar-btn:hover { background-color: #3a4050; border-color: #4caf50; }
    .ejemplar-btn-seleccionado {
        background-color: #4caf50;
        color: white;
        border-color: #4caf50;
    }
    h1, h2, h3, h4, h5, p, li, label { color: #eaeef2 !important; }
    .main-title {
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: #4caf50;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
    }
    .main-subtitle {
        text-align: center;
        color: #b0bec5;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    .stSidebar .stRadio label { color: #b0bec5 !important; font-size: 1rem; }
    .stSidebar .stRadio div[role="radiogroup"] label {
        background-color: #2a2f39;
        padding: 0.7rem 1rem;
        border-radius: 10px;
        margin: 4px 0;
        color: #ffffff !important;
        font-size: 1rem;
    }
    .stSidebar .stRadio div[role="radiogroup"] label:hover { background-color: #3a4050; }
    .stSidebar .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background-color: #4caf50;
        color: white !important;
    }
    .stSelectbox > div > div, .stTextInput > div > div, .stNumberInput > div > div {
        background-color: #2a2f39;
        color: #eaeef2;
        border-radius: 10px;
        border: 1px solid #3a4050;
        font-size: 1rem;
        padding: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #1e2229;
        padding: 0.5rem;
        border-radius: 12px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2a2f39;
        color: #b0bec5;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: bold;
        font-size: 0.9rem;
        flex: 1 1 auto;
        text-align: center;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #4caf50;
        color: white;
    }
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 70vh;
    }
    .login-box {
        background-color: #1e2229;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        max-width: 400px;
        width: 100%;
        border: 1px solid #2a2f39;
    }
    .login-box h1 { color: #4caf50; text-align: center; font-size: 1.8rem; margin-bottom: 0.5rem; }
    .login-box p { color: #b0bec5; text-align: center; margin-bottom: 1.5rem; }
    .login-box .stTextInput > div > div {
        background-color: #2a2f39 !important;
        border: 1px solid #3a4050 !important;
        font-size: 1rem;
        padding: 0.6rem;
    }
    .login-box .stButton > button {
        width: 100%;
        background-color: #4caf50;
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.8rem;
        border-radius: 12px;
        font-size: 1.1rem;
        transition: 0.3s;
    }
    .login-box .stButton > button:hover { background-color: #388e3c; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1e2229; }
    ::-webkit-scrollbar-thumb { background: #4caf50; border-radius: 3px; }
    .tabla-referencia {
        background-color: #1e2229;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid #3a4050;
    }
    .tabla-referencia th, .tabla-referencia td {
        padding: 0.5rem;
        text-align: center;
        border-bottom: 1px solid #2a2f39;
    }
    .tabla-referencia th {
        color: #4caf50;
        font-weight: bold;
    }
    @media (max-width: 768px) {
        .stColumns { flex-direction: column !important; }
        .stColumns > div { width: 100% !important; margin-bottom: 1rem; }
        .main-title { font-size: 1.6rem; }
        .tabla-referencia { font-size: 0.8rem; padding: 0.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# ---------- PWA: MANIFEST Y SERVICE WORKER ----------
st.markdown("""
<link rel="manifest" href="manifest.json">
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(() => console.log('Service Worker registrado'))
      .catch((err) => console.log('Error al registrar SW:', err));
  }
</script>
""", unsafe_allow_html=True)

# ---------- CONEXIÓN A SUPABASE ----------
@st.cache_resource
def init_supabase():
    url = st.secrets['PROJECT_URL'].strip().rstrip('/')
    key = st.secrets['API_SUPABASE'].strip()
    return create_client(url, key)

supabase = init_supabase()

# ---------- FUNCIÓN PARA RECUPERAR TOKEN DE VOICE MONKEY ----------
def obtener_token_voice_monkey(owner_name):
    """Recupera el token de Voice Monkey desde Supabase."""
    try:
        res = supabase.table("usuarios_tokens").select("token_voice_monkey").eq("owner_name", owner_name).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]['token_voice_monkey']
        else:
            return None
    except Exception as e:
        print(f"Error al obtener token: {e}")
        return None

# ---------- FUNCIÓN PARA ENVIAR NOTIFICACIÓN A VOICE MONKEY ----------
def enviar_notificacion_alexa(mensaje, owner_name):
    """
    Envía una notificación de voz a Alexa usando Voice Monkey.
    Retorna (éxito, mensaje).
    """
    token = obtener_token_voice_monkey(owner_name)
    if not token:
        return False, "No tienes token de Voice Monkey configurado. Ve a Configuración para agregarlo."
    
    url = "https://api-v2.voicemonkey.io/announcement"
    payload = {
        "token": token,
        "text": mensaje
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "📢 Notificación enviada a tu Alexa"
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error de conexión: {e}"

# ---------- RECOMENDACIÓN DE ALIMENTACIÓN ----------
def calcular_recomendacion_presa(peso_serpiente):
    """Calcula el rango de peso de la presa y la frecuencia según el peso."""
    if peso_serpiente is None or peso_serpiente <= 0:
        return {
            "rango_presa": "No disponible",
            "frecuencia": "Registra el peso para obtener recomendación",
            "peso_min": 0,
            "peso_max": 0,
            "etapa": "Sin datos"
        }
    
    if peso_serpiente < 500:
        porcentaje_min, porcentaje_max = 0.10, 0.15
        frecuencia = "cada 5-7 días"
        etapa = "Juvenil (<500g)"
    elif peso_serpiente < 1000:
        porcentaje_min, porcentaje_max = 0.07, 0.10
        frecuencia = "cada 7-10 días"
        etapa = "Sub-adulto (500-1000g)"
    else:
        porcentaje_min, porcentaje_max = 0.05, 0.07
        frecuencia = "cada 10-14 días"
        etapa = "Adulto (>1000g)"
    
    peso_min_presa = peso_serpiente * porcentaje_min
    peso_max_presa = peso_serpiente * porcentaje_max
    
    return {
        "rango_presa": f"{peso_min_presa:.0f}g - {peso_max_presa:.0f}g",
        "frecuencia": frecuencia,
        "peso_min": round(peso_min_presa),
        "peso_max": round(peso_max_presa),
        "etapa": etapa,
        "porcentaje_min": f"{porcentaje_min*100:.0f}%",
        "porcentaje_max": f"{porcentaje_max*100:.0f}%"
    }

# ---------- BASE DE CONOCIMIENTO ----------
SPECIES_DB = {
    "Boa constrictor": {
        "feed_interval": 10,
        "temp_range": (26, 32),
        "humidity": 60,
        "adult_weight": 5000,
        "shed_interval": 45,
        "diet": "Roedores (ratas, ratones)",
        "enclosure": "Terrario de 120x60x60 cm",
        "notes": "Requiere ramas para trepar y escondites.",
        "birth_weight": 50,
        "months_to_adult": 36,
        "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Rata", "Ratón", "Pollo", "Conejo"]
    },
    "Python regius": {
        "feed_interval": 7,
        "temp_range": (24, 30),
        "humidity": 55,
        "adult_weight": 2000,
        "shed_interval": 30,
        "diet": "Roedores (ratones pequeños)",
        "enclosure": "Terrario de 90x45x45 cm",
        "notes": "Necesita alta humedad durante la muda.",
        "birth_weight": 60,
        "months_to_adult": 24,
        "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Pinky", "Fuzzy", "Ratón pequeño", "Rata weanling", "Rata pequeña", "Rata mediana", "Rata grande"]
    },
    "Pantherophis guttatus": {
        "feed_interval": 5,
        "temp_range": (22, 28),
        "humidity": 40,
        "adult_weight": 800,
        "shed_interval": 20,
        "diet": "Roedores (ratones pequeños)",
        "enclosure": "Terrario de 60x40x40 cm",
        "notes": "Muy activo, necesita espacio para explorar.",
        "birth_weight": 10,
        "months_to_adult": 18,
        "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Ratón", "Pinky", "Fuzzy"]
    },
    "Lampropeltis getula": {
        "feed_interval": 7,
        "temp_range": (24, 29),
        "humidity": 50,
        "adult_weight": 1200,
        "shed_interval": 25,
        "diet": "Roedores, lagartijas",
        "enclosure": "Terrario de 90x45x45 cm",
        "notes": "Puede ser caníbal, mantener separados.",
        "birth_weight": 15,
        "months_to_adult": 20,
        "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Ratón", "Lagartija", "Pinky"]
    },
    "Morelia spilota": {
        "feed_interval": 10,
        "temp_range": (26, 32),
        "humidity": 60,
        "adult_weight": 3000,
        "shed_interval": 40,
        "diet": "Roedores y aves pequeñas",
        "enclosure": "Terrario alto (120x60x120 cm)",
        "notes": "Arborícola, necesita ramas y altura.",
        "birth_weight": 40,
        "months_to_adult": 30,
        "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Rata", "Ratón", "Pollo", "Codorniz"]
    },
    "Piton Bola": {
        "feed_interval": 7,
        "temp_range": (24, 30),
        "humidity": 55,
        "adult_weight": 2000,
        "shed_interval": 30,
        "diet": "Roedores (ratones pequeños)",
        "enclosure": "Terrario de 90x45x45 cm",
        "notes": "Especie común en cautiverio.",
        "birth_weight": 60,
        "months_to_adult": 24,
        "diet_type": "carnivoro",
        "alimentos_sugeridos": ["Pinky", "Fuzzy", "Ratón pequeño", "Rata weanling", "Rata pequeña", "Rata mediana", "Rata grande"]
    },
    "Pogona Viticeps": {
        "feed_interval": 1,
        "temp_range": (35, 40),
        "humidity": 30,
        "adult_weight": 500,
        "shed_interval": 14,
        "diet": "Insectos, verduras, frutas",
        "enclosure": "Terrario de 120x60x60 cm con luz UVB",
        "notes": "Necesita luz UVB y gradiente térmico.",
        "birth_weight": 5,
        "months_to_adult": 12,
        "diet_type": "omnivoro",
        "alimentos_sugeridos": ["Verdura", "Fruta", "Hojas verdes", "Insecto"]
    }
}
DEFAULT_SPECIES = {
    "feed_interval": 7,
    "temp_range": (25, 30),
    "humidity": 50,
    "adult_weight": 1000,
    "shed_interval": 30,
    "diet": "Roedores",
    "enclosure": "Terrario estándar",
    "notes": "Sin información adicional.",
    "birth_weight": 20,
    "months_to_adult": 24,
    "diet_type": "carnivoro",
    "alimentos_sugeridos": None
}

# ---------- CLASIFICACIÓN DE ALIMENTOS ----------
FOOD_CATEGORIES = {
    'insecto': [
        'grillo', 'tenebrio', 'gusano', 'cucaracha', 'langosta', 'saltamontes',
        'mosca', 'larva', 'zophoba', 'superworm', 'mealworm', 'cricket', 'roach',
        'hormiga', 'termita', 'escarabajo', 'polilla', 'gusano de seda', 'silk worm',
        'chapulín'
    ],
    'verdura': [
        'lechuga', 'zanahoria', 'calabacín', 'pepino', 'pimiento', 'brócoli', 'col',
        'espinaca', 'acelga', 'berza', 'diente de león', 'nopal', 'tuna', 'cardo',
        'calabaza', 'berenjena', 'judía verde', 'guisante', 'maíz', 'rábano', 'remolacha',
        'apio', 'esparrago', 'alcachofa', 'coliflor', 'repollo', 'col rizada', 'kale',
        'hoja de mostaza', 'hoja de nabo', 'perejil', 'cilantro', 'albahaca'
    ],
    'fruta': [
        'manzana', 'plátano', 'fresa', 'mango', 'papaya', 'pera', 'melón', 'sandía',
        'kiwi', 'uva', 'arándano', 'frambuesa', 'mora', 'cereza', 'durazno', 'ciruela',
        'higo', 'granada', 'pomelo', 'naranja', 'mandarina', 'limón', 'piña', 'coco',
        'maracuyá', 'guanábana', 'carambola', 'litchi', 'rambután'
    ]
}

def classify_food(food_text):
    if not food_text:
        return 'desconocido'
    food_lower = food_text.lower().strip()
    for categoria, keywords in FOOD_CATEGORIES.items():
        for kw in keywords:
            if kw in food_lower:
                return categoria
    if 'verdura' in food_lower or 'vegetal' in food_lower or 'hoja' in food_lower:
        return 'verdura'
    if 'fruta' in food_lower:
        return 'fruta'
    if 'insecto' in food_lower or 'bicho' in food_lower or 'proteína animal' in food_lower:
        return 'insecto'
    return 'otro'

# ---------- FUNCIONES AUXILIARES ----------
def get_species_info(species_name, weight=None):
    base = SPECIES_DB.get(species_name, DEFAULT_SPECIES)
    if weight is not None and weight > 0 and species_name in ["Python regius", "Piton Bola"]:
        rec = calcular_recomendacion_presa(weight)
        base = base.copy()
        base['feed_interval'] = rec.get('frecuencia', '7 días')
        base['presa_sugerida'] = rec.get('rango_presa', 'N/A')
        base['peso_presa_min'] = rec.get('peso_min', 0)
        base['peso_presa_max'] = rec.get('peso_max', 0)
        base['etapa'] = rec.get('etapa', 'N/A')
        base['porcentaje_min'] = rec.get('porcentaje_min', 'N/A')
        base['porcentaje_max'] = rec.get('porcentaje_max', 'N/A')
    return base

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
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def estimate_age(current_weight, species_info):
    birth_weight = species_info.get("birth_weight", 20)
    adult_weight = species_info.get("adult_weight", 1000)
    months_to_adult = species_info.get("months_to_adult", 24)
    if adult_weight <= birth_weight:
        return None
    if current_weight <= birth_weight:
        return 0
    if current_weight >= adult_weight:
        return months_to_adult
    proportion = (current_weight - birth_weight) / (adult_weight - birth_weight)
    return round(proportion * months_to_adult, 1)

# ---------- AUTENTICACIÓN ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.selected_reptile = None

if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-container">
        <div class="login-box">
            <h1>🦎 RIARE Exotic's</h1>
            <p>Gestión profesional de reptiles</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("👤 Nombre de Propietario", key="login_user", placeholder="Tu nombre", label_visibility="collapsed")
        if st.button("🚪 Ingresar", use_container_width=True):
            if username.strip():
                st.session_state.authenticated = True
                st.session_state.username = username.strip()
                st.rerun()
            else:
                st.error("Por favor, introduce un nombre.")
    st.stop()

# ---------- TÍTULO ----------
st.markdown('<div class="main-title">🦎 RIARE Exotic\'s</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Sistema de gestión herpetológica</div>', unsafe_allow_html=True)

# ---------- BARRA LATERAL ----------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/snake.png", width=80)
    st.title(f"👤 {st.session_state.username}")
    st.divider()
    menu = st.radio(
        "📌 Módulos",
        ["📊 Panel de Control", "➕ Nuevo Ejemplar", "🍽️ Alimentación", "🔄 Muda", "⚖️ Registro de Peso", "🏥 Veterinario", "⚙️ Configuración", "📈 Estadísticas Globales"],
        index=0
    )
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.selected_reptile = None
        st.rerun()
    st.caption("🐍 RIARE Exotic's v3.4")

# ---------- FUNCIONES DE CONSULTA ----------
@st.cache_data(ttl=60)
def get_reptiles(owner):
    try:
        res = supabase.table("reptiles").select("*").eq("owner_name", owner).execute()
        return res.data
    except:
        return []

@st.cache_data(ttl=60)
def get_events(table_name, unique_id):
    try:
        res = supabase.table(table_name).select("*").eq("unique_id", unique_id).order("fecha", desc=True).execute()
        return res.data
    except:
        return []

@st.cache_data(ttl=60)
def get_peso_history(unique_id):
    try:
        res = supabase.table("peso").select("*").eq("unique_id", unique_id).order("fecha", asc=True).execute()
        return res.data
    except:
        return []

# ---------- FUNCIÓN PARA MOSTRAR BOTONES DE EJEMPLAR ----------
def mostrar_botones_ejemplares(reptiles):
    if not reptiles:
        st.info("No hay ejemplares registrados.")
        return None
    
    cols = st.columns(2)
    selected_id = None
    
    for idx, r in enumerate(reptiles):
        col = cols[idx % 2]
        label = f"{r.get('name', 'Sin nombre')}\n({r.get('species', 'N/A')})"
        is_selected = (st.session_state.get('selected_reptile') == r['unique_id'])
        
        if col.button(label, key=f"btn_{r['unique_id']}", use_container_width=True):
            st.session_state.selected_reptile = r['unique_id']
            st.rerun()
    
    if st.session_state.selected_reptile:
        for r in reptiles:
            if r['unique_id'] == st.session_state.selected_reptile:
                return r
    return None

# ---------- PÁGINAS ----------

# ---- PANEL DE CONTROL ----
if menu == "📊 Panel de Control":
    st.header("📊 Panel de Control")
    reptiles = get_reptiles(st.session_state.username)

    if not reptiles:
        st.info("No hay ejemplares registrados. Ve a 'Nuevo Ejemplar' para agregar uno.")
    else:
        st.subheader("🦎 Selecciona un ejemplar")
        item = mostrar_botones_ejemplares(reptiles)
        
        if not item:
            st.warning("Selecciona un ejemplar de los botones arriba.")
        else:
            unique_id = item['unique_id']
            species_name = item.get('species', '')
            current_weight = safe_int(item.get('peso'))
            species_info = get_species_info(species_name, current_weight)

            alimentacion = get_events("alimentacion", unique_id)
            muda = get_events("muda", unique_id)
            veterinario = get_events("veterinario", unique_id)
            peso_hist = get_peso_history(unique_id)

            # ---- Métricas superiores ----
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🐍 Especie", species_name if species_name else "Desconocida")
            with col2:
                st.metric("⚖️ Peso actual", f"{current_weight} g")
            with col3:
                if alimentacion and len(alimentacion) > 0:
                    last_feed = alimentacion[0].get('fecha')
                    days = safe_days_between(last_feed)
                    st.metric("🍽️ Última alimentación", f"Hace {days} días" if days is not None else "N/A")
                else:
                    st.metric("🍽️ Última alimentación", "Sin registros")
            with col4:
                if muda and len(muda) > 0:
                    last_shed = muda[0].get('fecha')
                    days = safe_days_between(last_shed)
                    st.metric("🔄 Última muda", f"Hace {days} días" if days is not None else "N/A")
                else:
                    st.metric("🔄 Última muda", "Sin registros")

            st.divider()

            # ---- Información del ejemplar ----
            st.subheader("📋 Información del ejemplar")
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.write(f"**📛 Nombre:** {item.get('name', 'Sin nombre')}")
                st.write(f"**🔬 Especie:** {item.get('species', 'N/A')}")
                st.write(f"**🧬 Fase/Gen:** {item.get('fase', 'N/A')}")
            with col_info2:
                st.write(f"**⚥ Sexo:** {item.get('sex', 'N/A')}")
                st.write(f"**📄 Pedimento:** {item.get('pedimento', 'N/A')}")
                st.write(f"**📝 Notas:** {item.get('notas', 'N/A')}")

            st.divider()

            # ---- Recomendaciones personalizadas ----
            st.subheader("🧠 Recomendaciones personalizadas")
            with st.container():
                col_rec1, col_rec2 = st.columns([2, 1])
                with col_rec1:
                    # Alimentación dinámica
                    if species_name in ["Python regius", "Piton Bola"] and current_weight > 0:
                        rec = calcular_recomendacion_presa(current_weight)
                        st.success(f"📊 **Etapa:** {rec['etapa']}")
                        st.info(f"🍗 **Presa recomendada:** {rec['rango_presa']} (aprox. {rec['porcentaje_min']} - {rec['porcentaje_max']} del peso corporal)")
                        st.info(f"📅 **Frecuencia:** {rec['frecuencia']}")
                        
                        # Mostrar tabla comparativa
                        with st.expander("📖 Tabla comparativa de referencia (pitones bola)", expanded=True):
                            tabla_html = """
                            <div class="tabla-referencia">
                                <table style="width:100%; border-collapse: collapse;">
                                    <thead>
                                        <tr>
                                            <th>Etapa</th>
                                            <th>Peso de la serpiente</th>
                                            <th>% del peso corporal</th>
                                            <th>Frecuencia</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>🟢 Juvenil</td>
                                            <td>&lt; 500g</td>
                                            <td>10% - 15%</td>
                                            <td>cada 5-7 días</td>
                                        </tr>
                                        <tr>
                                            <td>🟡 Sub-adulto</td>
                                            <td>500g - 1000g</td>
                                            <td>7% - 10%</td>
                                            <td>cada 7-10 días</td>
                                        </tr>
                                        <tr>
                                            <td>🔴 Adulto</td>
                                            <td>&gt; 1000g</td>
                                            <td>5% - 7%</td>
                                            <td>cada 10-14 días</td>
                                        </tr>
                                    </tbody>
                                </table>
                                <p style="font-size:0.8rem; color:#b0bec5; margin-top:0.5rem;">
                                    💡 <strong>Nota:</strong> Estos valores son orientativos. Ajusta según la condición corporal de tu ejemplar.
                                </p>
                            </div>
                            """
                            st.markdown(tabla_html, unsafe_allow_html=True)
                        
                        # Comparar con la última alimentación
                        if alimentacion and len(alimentacion) > 0:
                            last_feed_date_str = alimentacion[0].get('fecha')
                            try:
                                last_feed_date = datetime.strptime(last_feed_date_str[:10], "%Y-%m-%d")
                                days_since = (datetime.now() - last_feed_date).days
                                freq_days = re.findall(r'\d+', rec['frecuencia'])
                                if freq_days:
                                    min_days = int(freq_days[0])
                                    max_days = int(freq_days[1]) if len(freq_days) > 1 else min_days
                                    if days_since > max_days:
                                        st.error(f"⚠️ **Alerta**: Han pasado **{days_since} días** desde la última alimentación. Debería comer {rec['frecuencia']}.")
                                        # --- ENVIAR NOTIFICACIÓN A ALEXA ---
                                        nombre_ejemplar = item.get('name', 'Ejemplar sin nombre')
                                        with st.spinner("Enviando notificación a Alexa..."):
                                            exito, mensaje_alexa = enviar_notificacion_alexa(
                                                f"Alerta de alimentación: {nombre_ejemplar} lleva {days_since} días sin comer. Intervalo recomendado: {rec['frecuencia']}.",
                                                st.session_state.username
                                            )
                                            if exito:
                                                st.success("📢 Notificación enviada a tu Alexa")
                                            else:
                                                st.info(f"ℹ️ {mensaje_alexa}")
                                    else:
                                        st.success(f"✅ Última alimentación hace {days_since} días. Intervalo recomendado: {rec['frecuencia']}.")
                            except:
                                pass
                    elif current_weight <= 0:
                        st.warning("⚠️ **Registra el peso del ejemplar** para obtener una recomendación precisa de alimentación.")
                    else:
                        st.info(f"ℹ️ Para {species_name}, consulta guías específicas de alimentación.")

                    # Muda
                    shed_interval = species_info.get("shed_interval", 30)
                    if muda and len(muda) > 0:
                        last_shed_date_str = muda[0].get('fecha')
                        try:
                            last_shed_date = datetime.strptime(last_shed_date_str[:10], "%Y-%m-%d")
                            next_shed_estimated = last_shed_date + timedelta(days=shed_interval)
                            days_until_shed = (next_shed_estimated - datetime.now()).days
                            if days_until_shed <= 0:
                                st.warning(f"🔄 Posible muda inminente (intervalo: {shed_interval} días).")
                            else:
                                st.info(f"🔄 Próxima muda estimada en {days_until_shed} días.")
                        except:
                            st.info("ℹ️ No se pudo calcular la próxima muda.")
                    else:
                        st.info(f"ℹ️ La especie {species_name} muda cada {shed_interval} días aprox.")

                    # Condiciones
                    temp_min, temp_max = species_info.get("temp_range", (25, 30))
                    hum = species_info.get("humidity", 50)
                    st.write(f"🌡️ **Condiciones ideales**: {temp_min}°C - {temp_max}°C, humedad ~{hum}%.")
                    st.write(f"🍽️ **Dieta general**: {species_info.get('diet', 'N/A')}")
                    st.write(f"🏠 **Terrario**: {species_info.get('enclosure', 'N/A')}")

                with col_rec2:
                    adult_weight = species_info.get("adult_weight", 1000)
                    if current_weight > 0:
                        progress = min(current_weight / adult_weight, 1.0)
                        st.metric("📈 Progreso", f"{current_weight}g / {adult_weight}g")
                        st.progress(progress, text=f"{progress*100:.1f}% adulto")
                    else:
                        st.info("Registra peso para ver progreso.")

            st.divider()

            # ---- Gráfico de dieta (omnívoros) ----
            if species_info.get("diet_type") == "omnivoro":
                st.subheader("🥗 Variabilidad de la dieta")
                if alimentacion and len(alimentacion) > 0:
                    df_alim = pd.DataFrame(alimentacion)
                    df_alim['categoria'] = df_alim['tipo_alimento'].apply(classify_food)
                    counts = df_alim['categoria'].value_counts().reset_index()
                    counts.columns = ['Categoría', 'Conteo']
                    fig = px.bar(counts, x='Categoría', y='Conteo', color='Categoría',
                                 title='Distribución de alimentos consumidos',
                                 labels={'Conteo': 'Número de registros'})
                    fig.update_layout(template='plotly_dark', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Detalle de alimentos"):
                        st.dataframe(df_alim[['fecha', 'tipo_alimento', 'categoria']].head(10), use_container_width=True)

                    if 'insecto' not in counts['Categoría'].values:
                        st.warning("⚠️ No se han registrado insectos. ¡Necesitan proteína animal!")
                    if 'verdura' not in counts['Categoría'].values:
                        st.warning("⚠️ No se han registrado verduras. ¡Incluye vegetales de hoja verde!")
                    if 'fruta' not in counts['Categoría'].values:
                        st.info("🍎 La fruta puede ofrecerse como premio ocasional.")
                else:
                    st.info("Registra alimentaciones para ver la variedad de la dieta.")
                st.divider()

            # ---- Gráfico de peso ----
            st.subheader("📈 Evolución de peso")
            if peso_hist and len(peso_hist) > 0:
                try:
                    df_peso = pd.DataFrame(peso_hist)
                    df_peso['fecha'] = pd.to_datetime(df_peso['fecha']).dt.date
                    df_peso = df_peso.sort_values('fecha')
                    fig = px.line(df_peso, x='fecha', y='peso',
                                  title='Evolución del peso (tabla Peso)',
                                  labels={'peso': 'Peso (g)', 'fecha': 'Fecha'})
                    fig.update_layout(template='plotly_dark')
                    fig.update_xaxes(tickformat="%Y-%m-%d")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.info(f"No se pudo generar el gráfico: {str(e)}")
            elif alimentacion and len(alimentacion) > 0:
                try:
                    df_alim = pd.DataFrame(alimentacion)
                    if 'peso_alimento' in df_alim.columns and not df_alim['peso_alimento'].isnull().all():
                        df_alim['fecha'] = pd.to_datetime(df_alim['fecha']).dt.date
                        df_alim = df_alim.sort_values('fecha')
                        fig = px.line(df_alim, x='fecha', y='peso_alimento',
                                      title='Evolución del peso (desde alimentación)',
                                      labels={'peso_alimento': 'Peso (g)', 'fecha': 'Fecha'})
                        fig.update_layout(template='plotly_dark')
                        fig.update_xaxes(tickformat="%Y-%m-%d")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No hay datos de peso en alimentación.")
                except Exception as e:
                    st.info(f"No se pudo generar el gráfico: {str(e)}")
            else:
                st.info("Registra pesos en 'Registro de Peso' para ver la evolución.")

            # ---- Historial ----
            st.subheader("📋 Historial completo")
            tabs = st.tabs(["🍽️ Alimentación", "🔄 Muda", "⚖️ Peso", "🏥 Veterinario"])

            with tabs[0]:
                if alimentacion:
                    df = pd.DataFrame(alimentacion)
                    df = df.drop(columns=['id', 'unique_id', 'owner_name'], errors='ignore')
                    if 'fecha' in df:
                        df['días desde'] = df['fecha'].apply(lambda x: safe_days_between(x) if safe_days_between(x) is not None else '')
                    if 'tipo_alimento' in df:
                        df['categoría'] = df['tipo_alimento'].apply(classify_food)
                    st.dataframe(df, use_container_width=True, height=300)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar CSV", data=csv, file_name=f"alimentacion_{unique_id}.csv", mime="text/csv")
                else:
                    st.info("Sin registros de alimentación.")

            with tabs[1]:
                if muda:
                    df = pd.DataFrame(muda)
                    df = df.drop(columns=['id', 'unique_id', 'owner_name'], errors='ignore')
                    if 'fecha' in df:
                        df['días desde'] = df['fecha'].apply(lambda x: safe_days_between(x) if safe_days_between(x) is not None else '')
                    st.dataframe(df, use_container_width=True, height=300)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar CSV", data=csv, file_name=f"muda_{unique_id}.csv", mime="text/csv")
                else:
                    st.info("Sin registros de muda.")

            with tabs[2]:
                if peso_hist:
                    df = pd.DataFrame(peso_hist)
                    df = df.drop(columns=['id', 'unique_id', 'owner_name'], errors='ignore')
                    if 'fecha' in df:
                        df['días desde'] = df['fecha'].apply(lambda x: safe_days_between(x) if safe_days_between(x) is not None else '')
                    st.dataframe(df, use_container_width=True, height=300)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar CSV", data=csv, file_name=f"peso_{unique_id}.csv", mime="text/csv")
                else:
                    st.info("Sin registros de peso.")

            with tabs[3]:
                if veterinario:
                    df = pd.DataFrame(veterinario)
                    df = df.drop(columns=['id', 'unique_id', 'owner_name'], errors='ignore')
                    if 'fecha' in df:
                        df['días desde'] = df['fecha'].apply(lambda x: safe_days_between(x) if safe_days_between(x) is not None else '')
                    st.dataframe(df, use_container_width=True, height=300)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar CSV", data=csv, file_name=f"veterinario_{unique_id}.csv", mime="text/csv")
                else:
                    st.info("Sin registros veterinarios.")

# ---- NUEVO EJEMPLAR ----
elif menu == "➕ Nuevo Ejemplar":
    st.header("➕ Registrar nuevo ejemplar")
    with st.form("new_reptile", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("📛 Nombre")
            species = st.text_input("🔬 Especie")
            sex = st.selectbox("⚥ Sexo", ["Macho", "Hembra", "Desconocido"])
            fase = st.text_input("🧬 Fase / Gen (opcional)", help="Ej: Albino, Pastel, Jaguar, etc.")
        with col2:
            pedimento = st.text_input("📄 Pedimento (opcional)")
            peso = st.number_input("⚖️ Peso (g)", min_value=0, step=50)
        notas = st.text_area("📝 Notas adicionales")
        
        submitted = st.form_submit_button("💾 Guardar ejemplar", use_container_width=True)
        if submitted:
            if species.strip() == "":
                st.error("La especie es obligatoria.")
            else:
                u_id = f"{species[:2].upper()}{random.randint(1000, 9999)}"
                data = {
                    "name": name,
                    "species": species,
                    "owner_name": st.session_state.username,
                    "sex": sex,
                    "unique_id": u_id,
                    "pedimento": pedimento,
                    "peso": int(peso),
                    "notas": notas,
                    "fase": fase
                }
                try:
                    supabase.table("reptiles").insert(data).execute()
                    st.success(f"✅ Ejemplar **{u_id}** registrado correctamente.")
                    st.cache_data.clear()
                    st.session_state.selected_reptile = u_id
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")

# ---- ALIMENTACIÓN ----
elif menu == "🍽️ Alimentación":
    st.header("🍽️ Registrar alimentación")
    reptiles = get_reptiles(st.session_state.username)
    if not reptiles:
        st.warning("Primero registra un ejemplar.")
    else:
        st.subheader("🦎 Selecciona un ejemplar")
        item = mostrar_botones_ejemplares(reptiles)
        
        if not item:
            st.warning("Selecciona un ejemplar de los botones arriba.")
        else:
            unique_id = item['unique_id']
            especie = item.get('species', '')
            species_info = get_species_info(especie)
            alimentos = species_info.get('alimentos_sugeridos', None)

            with st.form("feed_form"):
                fecha = st.date_input("📅 Fecha", value=datetime.now())
                if alimentos:
                    tipo_alimento = st.selectbox("🍗 Tipo de alimento", alimentos, help="Selecciona de la lista sugerida")
                else:
                    tipo_alimento = st.text_input("🍗 Tipo de alimento", help="Escribe el alimento")
                peso_alimento = st.number_input("⚖️ Peso del alimento (g)", min_value=0, step=5)
                notas = st.text_area("📝 Notas adicionales (opcional)")
                submitted = st.form_submit_button("💾 Guardar alimentación")
                if submitted:
                    if not tipo_alimento:
                        st.error("El tipo de alimento es obligatorio.")
                    else:
                        data = {
                            "unique_id": unique_id,
                            "owner_name": st.session_state.username,
                            "fecha": str(fecha),
                            "tipo_alimento": tipo_alimento,
                            "peso_alimento": int(peso_alimento)
                        }
                        try:
                            supabase.table("alimentacion").insert(data).execute()
                            st.success("✅ Alimentación registrada.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

# ---- MUDA ----
elif menu == "🔄 Muda":
    st.header("🔄 Registrar muda")
    reptiles = get_reptiles(st.session_state.username)
    if not reptiles:
        st.warning("Primero registra un ejemplar.")
    else:
        st.subheader("🦎 Selecciona un ejemplar")
        item = mostrar_botones_ejemplares(reptiles)
        
        if not item:
            st.warning("Selecciona un ejemplar de los botones arriba.")
        else:
            unique_id = item['unique_id']
            with st.form("shed_form"):
                fecha = st.date_input("📅 Fecha", value=datetime.now())
                comentarios = st.text_area("📝 Observaciones sobre la muda")
                submitted = st.form_submit_button("💾 Guardar muda")
                if submitted:
                    data = {
                        "unique_id": unique_id,
                        "owner_name": st.session_state.username,
                        "fecha": str(fecha),
                        "comentarios": comentarios
                    }
                    try:
                        supabase.table("muda").insert(data).execute()
                        st.success("✅ Muda registrada.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# ---- REGISTRO DE PESO ----
elif menu == "⚖️ Registro de Peso":
    st.header("⚖️ Registrar peso del ejemplar")
    reptiles = get_reptiles(st.session_state.username)
    if not reptiles:
        st.warning("Primero registra un ejemplar.")
    else:
        st.subheader("🦎 Selecciona un ejemplar")
        item = mostrar_botones_ejemplares(reptiles)
        
        if not item:
            st.warning("Selecciona un ejemplar de los botones arriba.")
        else:
            unique_id = item['unique_id']
            current_peso = safe_int(item.get('peso'))
            st.info(f"Peso actual registrado: **{current_peso} g**")
            with st.form("peso_form"):
                fecha = st.date_input("📅 Fecha", value=datetime.now())
                nuevo_peso = st.number_input("⚖️ Nuevo peso (g)", min_value=0, step=10, value=current_peso)
                notas = st.text_area("📝 Notas (opcional)")
                submitted = st.form_submit_button("💾 Guardar peso")
                if submitted:
                    if nuevo_peso <= 0:
                        st.error("El peso debe ser mayor a 0.")
                    else:
                        try:
                            data_peso = {
                                "unique_id": unique_id,
                                "owner_name": st.session_state.username,
                                "fecha": str(fecha),
                                "peso": int(nuevo_peso),
                                "notas": notas
                            }
                            supabase.table("peso").insert(data_peso).execute()
                            supabase.table("reptiles").update({"peso": int(nuevo_peso)}).eq("unique_id", unique_id).execute()
                            st.success(f"✅ Peso actualizado: {nuevo_peso} g")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al guardar peso: {e}")

# ---- VETERINARIO ----
elif menu == "🏥 Veterinario":
    st.header("🏥 Registrar visita veterinaria")
    reptiles = get_reptiles(st.session_state.username)
    if not reptiles:
        st.warning("Primero registra un ejemplar.")
    else:
        st.subheader("🦎 Selecciona un ejemplar")
        item = mostrar_botones_ejemplares(reptiles)
        
        if not item:
            st.warning("Selecciona un ejemplar de los botones arriba.")
        else:
            unique_id = item['unique_id']
            with st.form("vet_form"):
                fecha = st.date_input("📅 Fecha", value=datetime.now())
                evaluacion = st.text_area("🩺 Evaluación médica")
                tratamiento = st.text_input("💊 Tratamiento recetado")
                proxima_cita = st.date_input("📅 Próxima cita (opcional)", value=None)
                submitted = st.form_submit_button("💾 Guardar registro")
                if submitted:
                    data = {
                        "unique_id": unique_id,
                        "owner_name": st.session_state.username,
                        "fecha": str(fecha),
                        "evaluacion_medica": evaluacion,
                        "tratamiento": tratamiento,
                        "proxima_cita": str(proxima_cita) if proxima_cita else None
                    }
                    try:
                        supabase.table("veterinario").insert(data).execute()
                        st.success("✅ Registro veterinario guardado.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# ---- CONFIGURACIÓN (TOKEN DE VOICE MONKEY) ----
elif menu == "⚙️ Configuración":
    st.header("⚙️ Configuración de notificaciones")
    
    # Verificar si el usuario ya tiene token guardado
    token_actual = obtener_token_voice_monkey(st.session_state.username)
    if token_actual:
        st.success("✅ Tienes un token de Voice Monkey configurado.")
        st.info(f"Token actual: `{token_actual[:8]}...{token_actual[-4:]}` (oculto por seguridad)")
    else:
        st.warning("⚠️ Aún no has configurado tu token de Voice Monkey.")
    
    with st.form("token_form"):
        st.markdown("""
        ### 📢 Notificaciones por Alexa
        
        Para recibir notificaciones en tu dispositivo Alexa, necesitas un token de **Voice Monkey**.
        
        1. Ve a [Voice Monkey](https://voicemonkey.io) y regístrate.
        2. Vincula tu cuenta de Amazon (habilita la skill de Voice Monkey).
        3. Ve a **Settings → API Credentials** y copia tu **"Secret Token"**.
        4. Pega el token en el campo de abajo y guarda.
        """)
        
        token_input = st.text_input("🔑 Token de Voice Monkey", type="password", placeholder="Ej: abc123def456...")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 Guardar token", use_container_width=True)
        with col_btn2:
            if token_actual:
                delete_btn = st.form_submit_button("🗑️ Eliminar token", use_container_width=True)
        
        if submitted:
            if token_input.strip():
                # Guardar en Supabase
                data = {
                    "owner_name": st.session_state.username,
                    "token_voice_monkey": token_input.strip()
                }
                try:
                    supabase.table("usuarios_tokens").upsert(data, on_conflict="owner_name").execute()
                    st.success("✅ Token guardado correctamente. Ahora recibirás notificaciones en tu Alexa cuando haya alertas.")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar token: {e}")
            else:
                st.error("El token no puede estar vacío.")
        
        if token_actual and 'delete_btn' in locals() and delete_btn:
            try:
                supabase.table("usuarios_tokens").delete().eq("owner_name", st.session_state.username).execute()
                st.success("🗑️ Token eliminado correctamente. Ya no recibirás notificaciones.")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al eliminar token: {e}")
    
    # --- Probar notificación ---
    st.divider()
    st.subheader("🧪 Probar notificación")
    with st.form("test_notification"):
        mensaje_test = st.text_input("Mensaje de prueba", value="¡Hola! Esta es una notificación de prueba desde RIARE Exotic's.")
        submitted_test = st.form_submit_button("🔊 Enviar prueba a Alexa")
        if submitted_test:
            if token_actual:
                with st.spinner("Enviando notificación de prueba..."):
                    exito, mensaje = enviar_notificacion_alexa(mensaje_test, st.session_state.username)
                    if exito:
                        st.success("✅ ¡Notificación enviada! Deberías escucharla en tu Alexa en unos segundos.")
                    else:
                        st.error(f"❌ Error: {mensaje}")
            else:
                st.warning("⚠️ Primero debes configurar tu token de Voice Monkey para probar.")

# ---- ESTADÍSTICAS GLOBALES ----
elif menu == "📈 Estadísticas Globales":
    st.header("📈 Estadísticas globales")
    reptiles = get_reptiles(st.session_state.username)
    if not reptiles:
        st.info("No hay ejemplares para mostrar estadísticas.")
    else:
        total = len(reptiles)
        st.metric("📊 Total de ejemplares", total)

        df_species = pd.DataFrame(reptiles)
        if 'species' in df_species.columns:
            species_counts = df_species['species'].value_counts().reset_index()
            species_counts.columns = ['Especie', 'Cantidad']
            fig = px.bar(species_counts, x='Especie', y='Cantidad', title='Distribución por especie')
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)

        if 'sex' in df_species.columns:
            sex_counts = df_species['sex'].value_counts().reset_index()
            sex_counts.columns = ['Sexo', 'Cantidad']
            fig2 = px.pie(sex_counts, names='Sexo', values='Cantidad', title='Proporción por sexo')
            fig2.update_layout(template='plotly_dark')
            st.plotly_chart(fig2, use_container_width=True)

        if 'peso' in df_species.columns and 'species' in df_species.columns:
            avg_weight = df_species.groupby('species')['peso'].mean().reset_index()
            avg_weight.columns = ['Especie', 'Peso promedio (g)']
            fig3 = px.bar(avg_weight, x='Especie', y='Peso promedio (g)', title='Peso promedio por especie')
            fig3.update_layout(template='plotly_dark')
            st.plotly_chart(fig3, use_container_width=True)

        if 'fase' in df_species.columns:
            fase_counts = df_species['fase'].value_counts().reset_index()
            fase_counts.columns = ['Fase', 'Cantidad']
            fig_fase = px.bar(fase_counts, x='Fase', y='Cantidad', title='Distribución por fase/gen')
            fig_fase.update_layout(template='plotly_dark')
            st.plotly_chart(fig_fase, use_container_width=True)

        st.subheader("📅 Actividad reciente")
        all_events = []
        for table in ["alimentacion", "muda", "veterinario", "peso"]:
            for r in reptiles:
                uid = r['unique_id']
                data = get_events(table, uid) if table != "peso" else get_peso_history(uid)
                for ev in data:
                    all_events.append({
                        'fecha': ev.get('fecha'),
                        'tipo': table,
                        'unique_id': uid
                    })
        if all_events:
            df_events = pd.DataFrame(all_events)
            df_events = df_events.dropna(subset=['fecha'])
            if not df_events.empty:
                df_events['fecha'] = pd.to_datetime(df_events['fecha'])
                df_events['mes'] = df_events['fecha'].dt.to_period('M').astype(str)
                monthly = df_events.groupby(['mes', 'tipo']).size().reset_index(name='count')
                fig4 = px.bar(monthly, x='mes', y='count', color='tipo',
                              title='Eventos por mes y tipo',
                              labels={'mes': 'Mes', 'count': 'Número de eventos'})
                fig4.update_layout(template='plotly_dark')
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No hay eventos con fechas válidas.")
        else:
            st.info("No hay eventos registrados aún.")
