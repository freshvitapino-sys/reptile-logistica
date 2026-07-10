import streamlit as st
import os
from supabase import create_client
import pandas as pd
import random
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# ---------- CONFIGURACIÓN ----------
st.set_page_config(
    page_title="🐍 Herpeto-Logistics Pro",
    page_icon="🦎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        padding: 0 1rem;
    }
    .stApp {
        background-color: #f8f9fa;
    }
    .css-1d391kg {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #2e7d32;
    }
    .badge-warning {
        background-color: #ffc107;
        color: #000;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-danger {
        background-color: #dc3545;
        color: #fff;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-success {
        background-color: #28a745;
        color: #fff;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Conexión a Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets['PROJECT_URL'].strip().rstrip('/')
    key = st.secrets['API_SUPABASE'].strip()
    return create_client(url, key)

supabase = init_supabase()

# ---------- BASE DE CONOCIMIENTO DE ESPECIES ----------
SPECIES_DB = {
    "Boa constrictor": {
        "feed_interval": 10,        # días entre comidas
        "temp_range": (26, 32),     # °C
        "humidity": 60,
        "adult_weight": 5000,       # gramos
        "shed_interval": 45,        # días entre mudas
        "diet": "Roedores (ratas, ratones)",
        "enclosure": "Terrario de 120x60x60 cm",
        "notes": "Requiere ramas para trepar y escondites."
    },
    "Python regius": {
        "feed_interval": 7,
        "temp_range": (24, 30),
        "humidity": 55,
        "adult_weight": 2000,
        "shed_interval": 30,
        "diet": "Roedores (ratones pequeños)",
        "enclosure": "Terrario de 90x45x45 cm",
        "notes": "Necesita alta humedad durante la muda."
    },
    "Pantherophis guttatus": {
        "feed_interval": 5,
        "temp_range": (22, 28),
        "humidity": 40,
        "adult_weight": 800,
        "shed_interval": 20,
        "diet": "Roedores (ratones pequeños)",
        "enclosure": "Terrario de 60x40x40 cm",
        "notes": "Muy activo, necesita espacio para explorar."
    },
    "Lampropeltis getula": {
        "feed_interval": 7,
        "temp_range": (24, 29),
        "humidity": 50,
        "adult_weight": 1200,
        "shed_interval": 25,
        "diet": "Roedores, lagartijas",
        "enclosure": "Terrario de 90x45x45 cm",
        "notes": "Puede ser caníbal, mantener separados."
    },
    "Morelia spilota": {
        "feed_interval": 10,
        "temp_range": (26, 32),
        "humidity": 60,
        "adult_weight": 3000,
        "shed_interval": 40,
        "diet": "Roedores y aves pequeñas",
        "enclosure": "Terrario alto (120x60x120 cm)",
        "notes": "Arborícola, necesita ramas y altura."
    }
}

# Especie por defecto si no está en la base
DEFAULT_SPECIES = {
    "feed_interval": 7,
    "temp_range": (25, 30),
    "humidity": 50,
    "adult_weight": 1000,
    "shed_interval": 30,
    "diet": "Roedores",
    "enclosure": "Terrario estándar",
    "notes": "Sin información adicional."
}

# ---------- FUNCIONES AUXILIARES ----------
def get_species_info(species_name):
    """Retorna la información de la especie o la predeterminada."""
    return SPECIES_DB.get(species_name, DEFAULT_SPECIES)

def format_date(date_str):
    """Formatea fecha ISO a dd/mm/yyyy."""
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return date_str

def days_between(date_str):
    """Días transcurridos desde fecha dada."""
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return (datetime.now() - d).days
    except:
        return None

def estimate_next_event(dates_list, interval_days):
    """Estima la próxima fecha de un evento basado en el intervalo."""
    if not dates_list:
        return None
    # Tomamos la última fecha
    last_date = datetime.strptime(dates_list[0][:10], "%Y-%m-%d")
    next_date = last_date + timedelta(days=interval_days)
    return next_date

# ---------- AUTENTICACIÓN ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🐍 Acceso Profesional")
    col1, col2 = st.columns([1, 1])
    with col1:
        username = st.text_input("👤 Nombre de Propietario", placeholder="Tu nombre")
        password = st.text_input("🔒 Contraseña (opcional)", type="password", placeholder="Deja en blanco si no tienes")
        if st.button("🚪 Ingresar", use_container_width=True):
            # Validación simple (sin contraseña por ahora)
            if username.strip() != "":
                st.session_state.authenticated = True
                st.session_state.username = username.strip()
                st.rerun()
            else:
                st.error("Por favor, introduce un nombre.")
    st.stop()

# ---------- BARRA LATERAL ----------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/snake.png", width=80)
    st.title(f"👤 {st.session_state.username}")
    st.divider()
    
    menu = st.radio(
        "📌 Módulos",
        ["📊 Panel de Control", "➕ Nuevo Ejemplar", "🍽️ Alimentación", "🔄 Muda", "🏥 Veterinario", "📈 Estadísticas Globales"],
        index=0
    )
    
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    st.caption("🐍 Herpeto-Logistics Pro v2.0")

# ---------- PÁGINAS ----------

# Función para obtener todos los reptiles del usuario
@st.cache_data(ttl=60)
def get_reptiles(owner):
    res = supabase.table("reptiles").select("*").eq("owner_name", owner).execute()
    return res.data

# Función para obtener eventos de una tabla
@st.cache_data(ttl=60)
def get_events(table_name, unique_id):
    res = supabase.table(table_name).select("*").eq("unique_id", unique_id).order("fecha", desc=True).execute()
    return res.data

# ---- PANEL DE CONTROL ----
if menu == "📊 Panel de Control":
    st.header("📊 Panel de Control")
    reptiles = get_reptiles(st.session_state.username)
    
    if not reptiles:
        st.info("No hay ejemplares registrados. Ve a 'Nuevo Ejemplar' para agregar uno.")
    else:
        # Selección de ejemplar
        opciones = {f"{r['unique_id']} - {r.get('name', 'Sin nombre')} ({r.get('species', 'N/A')})": r for r in reptiles}
        selected_key = st.selectbox("🔍 Selecciona un ejemplar", list(opciones.keys()))
        item = opciones[selected_key]
        unique_id = item['unique_id']
        
        # Obtener datos de la especie
        species_name = item.get('species', '')
        species_info = get_species_info(species_name)
        
        # Obtener historiales
        alimentacion = get_events("alimentacion", unique_id)
        muda = get_events("muda", unique_id)
        veterinario = get_events("veterinario", unique_id)
        
        # ---- Métricas superiores ----
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🐍 Especie", species_name if species_name else "Desconocida")
        with col2:
            st.metric("⚖️ Peso actual", f"{item.get('peso', 0)} g")
        with col3:
            if alimentacion:
                last_feed = alimentacion[0]['fecha']
                days = days_between(last_feed)
                st.metric("🍽️ Última alimentación", f"Hace {days} días" if days is not None else "N/A")
            else:
                st.metric("🍽️ Última alimentación", "Sin registros")
        with col4:
            if muda:
                last_shed = muda[0]['fecha']
                days = days_between(last_shed)
                st.metric("🔄 Última muda", f"Hace {days} días" if days is not None else "N/A")
            else:
                st.metric("🔄 Última muda", "Sin registros")
        
        st.divider()
        
        # ---- Tarjeta de recomendaciones IA ----
        st.subheader("🧠 Recomendaciones personalizadas")
        with st.container():
            col_rec1, col_rec2 = st.columns([2, 1])
            with col_rec1:
                # Alimentación recomendada
                feed_interval = species_info.get("feed_interval", 7)
                if alimentacion:
                    last_feed_date = datetime.strptime(alimentacion[0]['fecha'][:10], "%Y-%m-%d")
                    next_feed_recommended = last_feed_date + timedelta(days=feed_interval)
                    days_until = (next_feed_recommended - datetime.now()).days
                    if days_until <= 0:
                        st.error(f"⚠️ **Alerta de alimentación**: ¡Han pasado {abs(days_until)} días desde la fecha recomendada para {species_name}! 🍽️")
                    else:
                        st.success(f"✅ Próxima alimentación recomendada en {days_until} días (según especie {species_name})")
                else:
                    st.info(f"ℹ️ Según la especie {species_name}, se recomienda alimentar cada {feed_interval} días. Registra la primera alimentación.")
                
                # Muda recomendada
                shed_interval = species_info.get("shed_interval", 30)
                if muda:
                    last_shed_date = datetime.strptime(muda[0]['fecha'][:10], "%Y-%m-%d")
                    next_shed_estimated = last_shed_date + timedelta(days=shed_interval)
                    days_until_shed = (next_shed_estimated - datetime.now()).days
                    if days_until_shed <= 0:
                        st.warning(f"🔄 Posible muda inminente (han pasado {abs(days_until_shed)} días desde el intervalo esperado).")
                    else:
                        st.info(f"🔄 Próxima muda estimada en {days_until_shed} días.")
                else:
                    st.info(f"ℹ️ La especie {species_name} suele mudar cada {shed_interval} días aproximadamente.")
                
                # Condiciones ambientales
                temp_min, temp_max = species_info.get("temp_range", (25, 30))
                hum = species_info.get("humidity", 50)
                st.write(f"🌡️ **Condiciones ideales**: {temp_min}°C - {temp_max}°C, humedad ~{hum}%.")
                st.write(f"🍽️ **Dieta recomendada**: {species_info.get('diet', 'N/A')}")
                st.write(f"🏠 **Terrario**: {species_info.get('enclosure', 'N/A')}")
                st.write(f"📝 **Notas**: {species_info.get('notes', '')}")
            
            with col_rec2:
                # Peso esperado (basado en adulto)
                adult_weight = species_info.get("adult_weight", 1000)
                current_weight = item.get('peso', 0)
                if current_weight > 0:
                    progress = min(current_weight / adult_weight, 1.0)
                    st.metric("📈 Progreso de peso", f"{current_weight}g / {adult_weight}g")
                    st.progress(progress, text=f"{progress*100:.1f}% del peso adulto")
                else:
                    st.info("Registra el peso para ver el progreso.")
                
                # Calcular edad aproximada (si se registró fecha de creación, usamos la fecha de alta)
                # En el registro no hay fecha de alta, pero podemos estimar desde el primer evento
                all_dates = []
                for ev in alimentacion + muda + veterinario:
                    if 'fecha' in ev:
                        all_dates.append(ev['fecha'])
                if all_dates:
                    first_date = min(all_dates)
                    days_old = days_between(first_date)
                    if days_old:
                        st.metric("📅 Edad estimada", f"{days_old // 30} meses" if days_old < 365 else f"{days_old // 365} años")
                else:
                    st.info("🕒 Edad no disponible (sin eventos).")
        
        st.divider()
        
        # ---- Gráficos ----
        st.subheader("📈 Evolución de peso")
        if alimentacion:
            # Extraer datos de peso de alimentación (si se registró peso_alimento)
            df_alim = pd.DataFrame(alimentacion)
            if 'peso_alimento' in df_alim.columns and not df_alim['peso_alimento'].isnull().all():
                df_alim['fecha'] = pd.to_datetime(df_alim['fecha'])
                df_alim = df_alim.sort_values('fecha')
                fig = px.line(df_alim, x='fecha', y='peso_alimento', 
                             title='Evolución del peso registrado en alimentaciones',
                             labels={'peso_alimento': 'Peso (g)', 'fecha': 'Fecha'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de peso en los registros de alimentación.")
        else:
            st.info("Registra alimentaciones para ver la evolución del peso.")
        
        # ---- Historial de eventos (tabs) ----
        st.subheader("📋 Historial completo")
        tabs = st.tabs(["🍽️ Alimentación", "🔄 Muda", "🏥 Veterinario"])
        
        # Tabla de alimentación
        with tabs[0]:
            if alimentacion:
                df = pd.DataFrame(alimentacion)
                df = df.drop(columns=['id', 'unique_id', 'owner_name'], errors='ignore')
                # Añadir columna de días desde
                df['días desde'] = df['fecha'].apply(lambda x: days_between(x) if days_between(x) is not None else '')
                st.dataframe(df, use_container_width=True, height=300)
                # Botón de descarga
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar CSV", data=csv, file_name=f"alimentacion_{unique_id}.csv", mime="text/csv")
            else:
                st.info("Sin registros de alimentación.")
        
        with tabs[1]:
            if muda:
                df = pd.DataFrame(muda)
                df = df.drop(columns=['id', 'unique_id', 'owner_name'], errors='ignore')
                df['días desde'] = df['fecha'].apply(lambda x: days_between(x) if days_between(x) is not None else '')
                st.dataframe(df, use_container_width=True, height=300)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar CSV", data=csv, file_name=f"muda_{unique_id}.csv", mime="text/csv")
            else:
                st.info("Sin registros de muda.")
        
        with tabs[2]:
            if veterinario:
                df = pd.DataFrame(veterinario)
                df = df.drop(columns=['id', 'unique_id', 'owner_name'], errors='ignore')
                df['días desde'] = df['fecha'].apply(lambda x: days_between(x) if days_between(x) is not None else '')
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
            name = st.text_input("📛 Nombre", placeholder="Ej: Loki")
            species = st.text_input("🔬 Especie", placeholder="Ej: Python regius")
            sex = st.selectbox("⚥ Sexo", ["Macho", "Hembra", "Desconocido"])
        with col2:
            pedimento = st.text_input("📄 Pedimento (opcional)")
            peso = st.number_input("⚖️ Peso (g)", min_value=0, step=50)
        notas = st.text_area("📝 Notas adicionales")
        
        submitted = st.form_submit_button("💾 Guardar ejemplar", use_container_width=True)
        if submitted:
            if species.strip() == "":
                st.error("La especie es obligatoria.")
            else:
                # Generar ID único
                u_id = f"{species[:2].upper()}{random.randint(1000, 9999)}"
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
                    st.success(f"✅ Ejemplar **{u_id}** registrado correctamente.")
                    # Limpiar caché
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")

# ---- ALIMENTACIÓN ----
elif menu == "🍽️ Alimentación":
    st.header("🍽️ Registrar alimentación")
    reptiles = get_reptiles(st.session_state.username)
    if not reptiles:
        st.warning("Primero registra un ejemplar.")
    else:
        opciones = {f"{r['unique_id']} - {r.get('name', 'Sin nombre')}": r for r in reptiles}
        selected = st.selectbox("Selecciona el ejemplar", list(opciones.keys()))
        item = opciones[selected]
        unique_id = item['unique_id']
        
        with st.form("feed_form"):
            fecha = st.date_input("📅 Fecha", value=datetime.now())
            tipo_alimento = st.text_input("🍗 Tipo de alimento", placeholder="Ej: Ratón adulto")
            peso_alimento = st.number_input("⚖️ Peso del alimento (g)", min_value=0, step=5)
            notas = st.text_area("📝 Notas adicionales")
            submitted = st.form_submit_button("💾 Guardar alimentación")
            if submitted:
                data = {
                    "unique_id": unique_id,
                    "owner_name": st.session_state.username,
                    "fecha": str(fecha),
                    "tipo_alimento": tipo_alimento,
                    "peso_alimento": int(peso_alimento),
                    "notas": notas
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
        opciones = {f"{r['unique_id']} - {r.get('name', 'Sin nombre')}": r for r in reptiles}
        selected = st.selectbox("Selecciona el ejemplar", list(opciones.keys()))
        item = opciones[selected]
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

# ---- VETERINARIO ----
elif menu == "🏥 Veterinario":
    st.header("🏥 Registrar visita veterinaria")
    reptiles = get_reptiles(st.session_state.username)
    if not reptiles:
        st.warning("Primero registra un ejemplar.")
    else:
        opciones = {f"{r['unique_id']} - {r.get('name', 'Sin nombre')}": r for r in reptiles}
        selected = st.selectbox("Selecciona el ejemplar", list(opciones.keys()))
        item = opciones[selected]
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

# ---- ESTADÍSTICAS GLOBALES ----
elif menu == "📈 Estadísticas Globales":
    st.header("📈 Estadísticas globales")
    reptiles = get_reptiles(st.session_state.username)
    if not reptiles:
        st.info("No hay ejemplares para mostrar estadísticas.")
    else:
        # Número total
        total = len(reptiles)
        st.metric("📊 Total de ejemplares", total)
        
        # Distribución por especie
        df_species = pd.DataFrame(reptiles)
        if 'species' in df_species.columns:
            species_counts = df_species['species'].value_counts().reset_index()
            species_counts.columns = ['Especie', 'Cantidad']
            fig = px.bar(species_counts, x='Especie', y='Cantidad', title='Distribución por especie')
            st.plotly_chart(fig, use_container_width=True)
        
        # Distribución por sexo
        if 'sex' in df_species.columns:
            sex_counts = df_species['sex'].value_counts().reset_index()
            sex_counts.columns = ['Sexo', 'Cantidad']
            fig2 = px.pie(sex_counts, names='Sexo', values='Cantidad', title='Proporción por sexo')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Peso promedio por especie
        if 'peso' in df_species.columns and 'species' in df_species.columns:
            avg_weight = df_species.groupby('species')['peso'].mean().reset_index()
            avg_weight.columns = ['Especie', 'Peso promedio (g)']
            fig3 = px.bar(avg_weight, x='Especie', y='Peso promedio (g)', title='Peso promedio por especie')
            st.plotly_chart(fig3, use_container_width=True)
        
        # Actividad reciente: número de eventos por mes (todas las tablas)
        st.subheader("📅 Actividad reciente")
        # Obtener todos los eventos de todas las tablas de todos los reptiles
        all_events = []
        for table in ["alimentacion", "muda", "veterinario"]:
            for r in reptiles:
                uid = r['unique_id']
                data = get_events(table, uid)
                for ev in data:
                    all_events.append({
                        'fecha': ev['fecha'],
                        'tipo': table,
                        'unique_id': uid
                    })
        if all_events:
            df_events = pd.DataFrame(all_events)
            df_events['fecha'] = pd.to_datetime(df_events['fecha'])
            df_events['mes'] = df_events['fecha'].dt.to_period('M').astype(str)
            # Conteo por mes y tipo
            monthly = df_events.groupby(['mes', 'tipo']).size().reset_index(name='count')
            fig4 = px.bar(monthly, x='mes', y='count', color='tipo', 
                         title='Eventos por mes y tipo',
                         labels={'mes': 'Mes', 'count': 'Número de eventos'})
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No hay eventos registrados aún.")
