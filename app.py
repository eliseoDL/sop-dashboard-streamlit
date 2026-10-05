import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================================================
# 1. CONFIGURACIÓN GENERAL
# =============================================================
st.set_page_config(page_title="S&OP Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Tablero S&OP: Plan Maestro de Producción")
st.markdown("Visión integrada de capacidad, volumen comercial y secuenciación en piso de planta.")

# =============================================================
# 2. PANEL LATERAL (PARÁMETROS)
# =============================================================
st.sidebar.header("⚙️ Parámetros de Planificación")

dias_laborables = st.sidebar.number_input("Días laborables (Mes)", min_value=1, max_value=31, value=22)
turnos = st.sidebar.selectbox("Esquema de Turnos", options=["1 Turno (8 hs)", "2 Turnos (16 hs)", "3 Turnos (24 hs)"], index=1)
horas_por_turno = int(turnos.split(" ")[0]) * 8

st.sidebar.divider()
st.sidebar.markdown("**Arranque Operativo**")
fecha_seleccionada = st.sidebar.date_input("Fecha de inicio", value=datetime.today())
hora_turno = st.sidebar.time_input("Hora primer turno", value=pd.to_datetime("06:00").time())
fecha_base = pd.to_datetime(f"{fecha_seleccionada} {hora_turno}")

# =============================================================
# 3. MOTOR DE DATOS
# =============================================================
@st.cache_data
def cargar_datos():
    return pd.read_csv('cronograma_produccion_pulp.csv')

try:
    df = cargar_datos()
    
    # Tiempos
    df['Inicio_dt'] = fecha_base + pd.to_timedelta(df['Inicio (hs)'], unit='h')
    df['Fin_dt'] = fecha_base + pd.to_timedelta(df['Fin (hs)'], unit='h')
    df['Duracion_hs'] = df['Fin (hs)'] - df['Inicio (hs)']
    df['Fecha_Corte'] = df['Inicio_dt'].dt.date
    
    # Traducción de Tiempos a Volúmenes Comerciales (Litros)
    # TK-100 rinde 4000L por lote, TK-200 rinde 2000L por lote
    df['Volumen_Lts'] = df['Tanque'].apply(lambda x: 4000 if x == 'TK-100' else 2000)
    
    # Capacidad Dinámica
    cantidad_equipos = df['Tanque'].nunique()
    capacidad_diaria_planta = cantidad_equipos * horas_por_turno
    capacidad_mensual_hs = capacidad_diaria_planta * dias_laborables
    
    # KPIs Globales
    volumen_total = df['Volumen_Lts'].sum()
    horas_totales = df['Duracion_hs'].sum()
    ocupacion_pct = (horas_totales / capacidad_mensual_hs) * 100

except FileNotFoundError:
    st.warning("No se encontró el archivo de planificación. Ejecutá el algoritmo MILP primero.")
    st.stop()

# =============================================================
# 4. ESTRUCTURA DE PESTAÑAS (TABS)
# =============================================================
tab_gerencia, tab_planta = st.tabs(["📊 Visión Gerencial", "⚙️ Operaciones en Planta"])

# -------------------------------------------------------------
# PESTAÑA 1: VISIÓN GERENCIAL (S&OP)
# -------------------------------------------------------------
with tab_gerencia:
    st.markdown("### Indicadores Clave de Desempeño (KPIs)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Volumen Planificado", f"{volumen_total:,.0f} Lts".replace(',', '.'))
    with col2:
        st.metric("Lotes Totales", len(df))
    with col3:
        st.metric("Carga de Máquina (Hs)", f"{horas_totales:.1f} hs")
    with col4:
        delta_color = "normal" if ocupacion_pct <= 85 else "inverse"
        st.metric("Saturación de Planta", f"{ocupacion_pct:.1f}%", 
                  delta="Riesgo Operativo" if ocupacion_pct > 85 else "Capacidad Disponible", 
                  delta_color=delta_color)

    st.divider()
    
    # Gráfico de barras combinando Volúmenes y Tiempos
    st.markdown("### Curva de Producción Proyectada (Volumen vs Tiempo)")
    
    df_diario = df.groupby('Fecha_Corte').agg({'Volumen_Lts': 'sum', 'Duracion_hs': 'sum'}).reset_index()
    
    fig_volumen = px.bar(
        df_diario, 
        x='Fecha_Corte', 
        y='Volumen_Lts',
        text_auto='.2s',
        labels={'Fecha_Corte': 'Día', 'Volumen_Lts': 'Litros Producidos'},
        color='Duracion_hs',
        color_continuous_scale='Blues',
        title="Litros diarios a despachar (El color más oscuro indica mayor carga de horas)"
    )
    fig_volumen.update_layout(xaxis_title="", yaxis_title="Litros")
    st.plotly_chart(fig_volumen, use_container_width=True)

# -------------------------------------------------------------
# PESTAÑA 2: OPERACIONES EN PLANTA (GANTT Y TABLA)
# -------------------------------------------------------------
with tab_planta:
    st.markdown("### Cronograma de Equipos (Makespan)")
    
    fig_gantt = px.timeline(
        df, 
        x_start="Inicio_dt", 
        x_end="Fin_dt", 
        y="Tanque",
        color="Lote",
        hover_data={"Volumen_Lts": True, "Duracion_hs": True, "Inicio (hs)": False, "Fin (hs)": False}
    )
    
    fig_gantt.update_yaxes(autorange="reversed")
    
    # Gantt ultra compacto
    fig_gantt.update_layout(
        showlegend=False, 
        height=250, 
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="", 
        yaxis_title="",
        xaxis=dict(
            range=[df['Inicio_dt'].min(), df['Fin_dt'].max()],
            tickformat="%d/%m\n%H:%M", 
            dtick=86400000, 
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)'
        )
    )
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    st.divider()
    
    st.markdown("### Hoja de Ruta Auditable")
    tabla_limpia = df[['Tanque', 'Lote', 'Volumen_Lts', 'Inicio_dt', 'Fin_dt', 'Duracion_hs']].copy()
    tabla_limpia.rename(columns={'Inicio_dt': 'Inicio', 'Fin_dt': 'Fin', 'Duracion_hs': 'Hs'}, inplace=True)
    tabla_limpia['Inicio'] = tabla_limpia['Inicio'].dt.strftime('%d/%m %H:%M')
    tabla_limpia['Fin'] = tabla_limpia['Fin'].dt.strftime('%d/%m %H:%M')
    
    st.dataframe(tabla_limpia, use_container_width=True, hide_index=True)