import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =============================================================
st.set_page_config(page_title="S&OP | Secuenciación de Planta", layout="wide", initial_sidebar_state="expanded")

st.title("🏭 Tablero de Control S&OP: Optimización de Reactores")
st.markdown("Herramienta de apoyo para la planificación operativa y asignación óptima de capacidad.")

# =============================================================
# 2. PANEL LATERAL - PARÁMETROS DEL MES Y TURNOS
# =============================================================
st.sidebar.header("⚙️ Configuración del Mes")

dias_laborables = st.sidebar.number_input("Días laborables en el mes", min_value=1, max_value=31, value=22)
turnos = st.sidebar.selectbox("Esquema de turnos", options=["1 Turno (8 hs)", "2 Turnos (16 hs)", "3 Turnos (24 hs)"], index=1)

horas_por_turno = int(turnos.split(" ")[0]) * 8

st.sidebar.divider()
st.sidebar.markdown("**Arranque Operativo**")
fecha_seleccionada = st.sidebar.date_input("Fecha de inicio del plan", value=datetime.today())
hora_turno = st.sidebar.time_input("Hora del primer turno", value=pd.to_datetime("06:00").time())
fecha_base = pd.to_datetime(f"{fecha_seleccionada} {hora_turno}")

# =============================================================
# 3. CARGA Y TRANSFORMACIÓN DE DATOS
# =============================================================
@st.cache_data
def cargar_datos():
    return pd.read_csv('cronograma_produccion_pulp.csv')

try:
    df_gantt = cargar_datos()
    
    # Fechas exactas de inicio y fin para cada lote
    df_gantt['Inicio_dt'] = fecha_base + pd.to_timedelta(df_gantt['Inicio (hs)'], unit='h')
    df_gantt['Fin_dt'] = fecha_base + pd.to_timedelta(df_gantt['Fin (hs)'], unit='h')
    df_gantt['Duracion_hs'] = df_gantt['Fin (hs)'] - df_gantt['Inicio (hs)']
    
    # Cálculo dinámico de capacidad instalada
    cantidad_equipos = df_gantt['Tanque'].nunique()
    capacidad_diaria_planta = cantidad_equipos * horas_por_turno
    capacidad_mensual_hs = capacidad_diaria_planta * dias_laborables
    
    horas_totales_usadas = df_gantt['Duracion_hs'].sum()
    ocupacion_pct = (horas_totales_usadas / capacidad_mensual_hs) * 100

except FileNotFoundError:
    st.error("No se encontró el archivo 'cronograma_produccion_pulp.csv'. Ejecutá primero el algoritmo.")
    st.stop()

# =============================================================
# 4. PANELES DE INDICADORES GERENCIALES (KPIs)
# =============================================================
st.markdown("### Resumen de Capacidad Mensual")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Capacidad Total Mensual", value=f"{capacidad_mensual_hs} hs", help=f"Calculado sobre {cantidad_equipos} equipos activos.")
with col2:
    st.metric(label="Horas de Proceso (Netas)", value=f"{horas_totales_usadas:.1f} hs")
with col3:
    delta_color = "normal" if ocupacion_pct <= 90 else "inverse"
    st.metric(label="Ocupación Total", value=f"{ocupacion_pct:.1f}%", delta="Riesgo de cuello de botella" if ocupacion_pct > 90 else "Capacidad holgada", delta_color=delta_color)
with col4:
    st.metric(label="Lotes Programados", value=len(df_gantt))

st.divider()

# =============================================================
# 5. DIAGRAMA DE GANTT COMPACTO (PLOTLY)
# =============================================================
st.markdown("### Distribución Operativa (Línea de Tiempo Mensual)")

fig_gantt = px.timeline(
    df_gantt, 
    x_start="Inicio_dt", 
    x_end="Fin_dt", 
    y="Tanque",
    color="Lote",
    hover_data={"Lote": True, "Duracion_hs": True, "Inicio (hs)": False, "Fin (hs)": False}
)

fig_gantt.update_yaxes(autorange="reversed")

# Recortamos el gráfico exactamente al primer y último lote
fecha_min = df_gantt['Inicio_dt'].min()
fecha_max = df_gantt['Fin_dt'].max()

fig_gantt.update_layout(
    showlegend=True, 
    height=300, # Altura más compacta
    margin=dict(l=0, r=0, t=30, b=0), # Eliminamos márgenes muertos
    xaxis_title="", # Sacamos el título del eje X para ahorrar espacio
    yaxis_title="Equipos",
    xaxis=dict(
        range=[fecha_min, fecha_max], # Fuerzo a que no haya espacio vacío a los costados
        tickformat="%d/%m\n%H:%M", 
        dtick=86400000, # Marca de 24 hs
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.3)',
        gridwidth=1
    )
)

st.plotly_chart(fig_gantt, use_container_width=True)
st.divider()

# =============================================================
# 6. TABLA DE DATOS AUDITABLE
# =============================================================
st.markdown("### Detalle Operativo de Secuenciación")

tabla_limpia = df_gantt[['Tanque', 'Lote', 'Inicio_dt', 'Fin_dt', 'Duracion_hs']].copy()
tabla_limpia.rename(columns={'Inicio_dt': 'Inicio', 'Fin_dt': 'Fin', 'Duracion_hs': 'Horas'}, inplace=True)
tabla_limpia['Inicio'] = tabla_limpia['Inicio'].dt.strftime('%Y-%m-%d %H:%M')
tabla_limpia['Fin'] = tabla_limpia['Fin'].dt.strftime('%Y-%m-%d %H:%M')

st.dataframe(tabla_limpia, use_container_width=True)