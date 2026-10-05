import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =============================================================
st.set_page_config(page_title="S&OP | Secuenciación de Planta", layout="wide", initial_sidebar_state="expanded")

st.title("🏭 Tablero de Control S&OP: Optimización de Reactores")
st.markdown("Herramienta de apoyo para la planificación operativa, asignación óptima de capacidad y control de eficiencia.")

# =============================================================
# 2. PANEL LATERAL - PARÁMETROS DEL MES Y TURNOS
# =============================================================
st.sidebar.header("⚙️ Configuración del Mes")

# Parámetros de capacidad instalada (Visión Gerencial)
dias_laborables = st.sidebar.number_input("Días laborables en el mes", min_value=1, max_value=31, value=22)
turnos = st.sidebar.selectbox("Esquema de turnos", options=["1 Turno (8 hs)", "2 Turnos (16 hs)", "3 Turnos (24 hs)"], index=1)

# Extraemos el número de horas según el texto seleccionado
horas_por_turno = int(turnos.split(" ")[0]) * 8
capacidad_mensual_hs = dias_laborables * horas_por_turno

st.sidebar.divider()

# Parámetros de inicio operativo (Visión de Planta)
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
    
    # Cálculos de fechas dinámicas
    df_gantt['Inicio_dt'] = fecha_base + pd.to_timedelta(df_gantt['Inicio (hs)'], unit='h')
    df_gantt['Fin_dt'] = fecha_base + pd.to_timedelta(df_gantt['Fin (hs)'], unit='h')
    df_gantt['Duracion_hs'] = df_gantt['Fin (hs)'] - df_gantt['Inicio (hs)']
    
    makespan_total = df_gantt['Fin (hs)'].max()
    total_lotes = len(df_gantt)
    
    # Cálculo de Ocupación de Planta
    ocupacion_pct = (makespan_total / capacidad_mensual_hs) * 100

except FileNotFoundError:
    st.error("No se encontró el archivo 'cronograma_produccion_pulp.csv'. Ejecutá primero el algoritmo.")
    st.stop()

# =============================================================
# 4. PANELES DE INDICADORES GERENCIALES (KPIs)
# =============================================================
st.markdown("### Resumen de Capacidad Mensual")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Capacidad Total Mensual", value=f"{capacidad_mensual_hs} hs")
with col2:
    st.metric(label="Horas Utilizadas (Makespan)", value=f"{makespan_total:.1f} hs")
with col3:
    delta_color = "normal" if ocupacion_pct <= 90 else "inverse"
    st.metric(label="Ocupación de Planta", value=f"{ocupacion_pct:.1f}%", delta="Riesgo de saturación" if ocupacion_pct > 90 else "Capacidad holgada", delta_color=delta_color)
with col4:
    st.metric(label="Lotes Programados", value=total_lotes)

st.divider()

# =============================================================
# 5. DIAGRAMA DE GANTT INTERACTIVO (PLOTLY)
# =============================================================
st.markdown("### Distribución Operativa (Secuencia MILP)")

fig_gantt = px.timeline(
    df_gantt, 
    x_start="Inicio_dt", 
    x_end="Fin_dt", 
    y="Tanque",
    color="Lote",
    hover_data={
        "Lote": True,
        "Tanque": False,
        "Inicio_dt": "|%d/%m %H:%M",
        "Fin_dt": "|%d/%m %H:%M",
        "Duracion_hs": True,
        "Inicio (hs)": False,
        "Fin (hs)": False
    }
)

fig_gantt.update_yaxes(autorange="reversed")
fig_gantt.update_layout(
    showlegend=True, 
    height=400, 
    xaxis_title="Calendario Operativo", 
    yaxis_title="Equipos",
    hovermode="closest"
)

st.plotly_chart(fig_gantt, use_container_width=True)
st.divider()

# =============================================================
# 6. ANÁLISIS DE EFICIENCIA DIARIA
# =============================================================
st.markdown("### Eficiencia de Ocupación Diaria")

# Extraemos solo la fecha (sin la hora) de cada lote
df_gantt['Fecha_Corte'] = df_gantt['Inicio_dt'].dt.date

# Sumamos cuántas horas trabajó la planta cada día en total
uso_diario = df_gantt.groupby('Fecha_Corte')['Duracion_hs'].sum().reset_index()

# Calculamos la capacidad máxima diaria (2 tanques * horas del turno)
capacidad_diaria_maquina = 2 * horas_por_turno
uso_diario['Eficiencia (%)'] = (uso_diario['Duracion_hs'] / capacidad_diaria_maquina) * 100

# Armamos el gráfico de barras
fig_eficiencia = px.bar(
    uso_diario, 
    x='Fecha_Corte', 
    y='Eficiencia (%)',
    text_auto='.1f',
    labels={'Fecha_Corte': 'Día Operativo', 'Eficiencia (%)': '% de Eficiencia'},
    color='Eficiencia (%)',
    color_continuous_scale='RdYlGn'
)

# Línea roja marcando el 100% de la capacidad física
fig_eficiencia.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Capacidad Instalada (100%)")
fig_eficiencia.update_layout(yaxis_range=[0, max(uso_diario['Eficiencia (%)'].max() + 10, 110)])

st.plotly_chart(fig_eficiencia, use_container_width=True)

# =============================================================
# 7. TABLA DE DATOS AUDITABLE
# =============================================================
st.markdown("### Detalle Operativo de Secuenciación")

tabla_limpia = df_gantt[['Tanque', 'Lote', 'Inicio_dt', 'Fin_dt', 'Duracion_hs']].copy()
tabla_limpia.rename(columns={'Inicio_dt': 'Fecha/Hora Inicio', 'Fin_dt': 'Fecha/Hora Fin', 'Duracion_hs': 'Duración (hs)'}, inplace=True)
tabla_limpia['Fecha/Hora Inicio'] = tabla_limpia['Fecha/Hora Inicio'].dt.strftime('%Y-%m-%d %H:%M')
tabla_limpia['Fecha/Hora Fin'] = tabla_limpia['Fecha/Hora Fin'].dt.strftime('%Y-%m-%d %H:%M')

st.dataframe(tabla_limpia, use_container_width=True)