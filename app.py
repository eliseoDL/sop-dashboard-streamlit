import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =============================================================
st.set_page_config(page_title="S&OP | Secuenciación de Planta", layout="wide", initial_sidebar_state="expanded")

st.title("🏭 Tablero de Control S&OP: Optimización de Reactores")
st.markdown("Herramienta de apoyo para la planificación operativa, asignación óptima de capacidad y control de eficiencia diaria.")

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
    
    # -------------------------------------------------------------
    # CÁLCULO DINÁMICO DE CAPACIDAD INSTALADA
    # -------------------------------------------------------------
    # 1. Detectamos cuántos equipos distintos están operando en el CSV
    cantidad_equipos = df_gantt['Tanque'].nunique()
    
    # 2. Capacidad Diaria = (Cant. Equipos) x (Horas del Turno)
    capacidad_diaria_planta = cantidad_equipos * horas_por_turno
    
    # 3. Capacidad Mensual = Capacidad Diaria x Días Laborables
    capacidad_mensual_hs = capacidad_diaria_planta * dias_laborables
    
    # Horas totales de proceso reales (suma de todos los lotes)
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
# 5. DIAGRAMA DE GANTT (CON GRILLA DIARIA)
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

# Forzamos la cuadrícula de 24 horas (86400000 milisegundos)
fig_gantt.update_layout(
    showlegend=True, 
    height=400, 
    xaxis_title="Calendario Operativo", 
    yaxis_title="Equipos",
    xaxis=dict(
        tickformat="%d/%m\n%H:%M", 
        dtick=86400000, 
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.3)',
        gridwidth=1
    )
)

st.plotly_chart(fig_gantt, use_container_width=True)
st.divider()

# =============================================================
# 6. ANÁLISIS DE EFICIENCIA DIARIA (MES COMPLETO)
# =============================================================
st.markdown("### Eficiencia de Ocupación Diaria")

# 1. Sumamos horas por día
df_gantt['Fecha_Corte'] = df_gantt['Inicio_dt'].dt.date
uso_diario = df_gantt.groupby('Fecha_Corte')['Duracion_hs'].sum().reset_index()

# 2. Generamos el calendario completo del mes
fecha_inicio_plan = df_gantt['Fecha_Corte'].min()
rango_mes = pd.date_range(start=fecha_inicio_plan, periods=dias_laborables).date

# 3. Alineamos los datos (los días vacíos se rellenan con 0 horas)
uso_diario = uso_diario.set_index('Fecha_Corte').reindex(rango_mes, fill_value=0).reset_index()
uso_diario.columns = ['Fecha_Corte', 'Duracion_hs']

# 4. Calculamos eficiencia usando la Capacidad Diaria Dinámica
uso_diario['Eficiencia (%)'] = (uso_diario['Duracion_hs'] / capacidad_diaria_planta) * 100

# 5. Gráfico de barras
fig_eficiencia = px.bar(
    uso_diario, 
    x='Fecha_Corte', 
    y='Eficiencia (%)',
    text_auto='.1f',
    labels={'Fecha_Corte': 'Día del Mes', 'Eficiencia (%)': '% de Eficiencia'},
    color='Eficiencia (%)',
    color_continuous_scale='RdYlGn',
    range_color=[0, 100]
)

fig_eficiencia.add_hline(y=100, line_dash="dash", line_color="red", annotation_text=f"Capacidad Máxima ({capacidad_diaria_planta} hs)")

fig_eficiencia.update_layout(
    yaxis_range=[0, max(uso_diario['Eficiencia (%)'].max() + 10, 110)],
    xaxis=dict(
        tickmode='linear', 
        dtick=86400000 # Fuerza a mostrar todos los días sin saltear etiquetas
    )
)

st.plotly_chart(fig_eficiencia, use_container_width=True)

# =============================================================
# 7. TABLA DE DATOS 
# =============================================================
st.markdown("### Detalle Operativo de Secuenciación")

tabla_limpia = df_gantt[['Tanque', 'Lote', 'Inicio_dt', 'Fin_dt', 'Duracion_hs']].copy()
tabla_limpia.rename(columns={'Inicio_dt': 'Inicio', 'Fin_dt': 'Fin', 'Duracion_hs': 'Horas'}, inplace=True)
tabla_limpia['Inicio'] = tabla_limpia['Inicio'].dt.strftime('%Y-%m-%d %H:%M')
tabla_limpia['Fin'] = tabla_limpia['Fin'].dt.strftime('%Y-%m-%d %H:%M')

st.dataframe(tabla_limpia, use_container_width=True)