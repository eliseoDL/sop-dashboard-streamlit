import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# =============================================================
# 1. CONFIGURACIÓN GENERAL
# =============================================================
st.set_page_config(page_title="S&OP Dashboard", layout="wide", initial_sidebar_state="expanded")

st.title("🏭 Tablero S&OP: Plan Maestro de Producción")
st.markdown("Visión integrada de capacidad neta, volumen comercial y eficiencia de equipos.")

# =============================================================
# 2. PANEL LATERAL (PARÁMETROS Y DISPONIBILIDAD)
# =============================================================
st.sidebar.header("⚙️ Parámetros de Calendario")

dias_mes = st.sidebar.number_input("Días totales del mes", min_value=28, max_value=31, value=30)
dias_inactivos = st.sidebar.number_input("Días inactivos (Feriados/Paradas)", min_value=0, max_value=15, value=4, help="Fines de semana o días sin operación total.")
dias_laborables = dias_mes - dias_inactivos

turnos = st.sidebar.selectbox("Esquema de Turnos", options=["1 Turno (8 hs)", "2 Turnos (16 hs)", "3 Turnos (24 hs)"], index=1)
horas_por_turno = int(turnos.split(" ")[0]) * 8

st.sidebar.divider()
st.sidebar.markdown("**Arranque Operativo**")
fecha_seleccionada = st.sidebar.date_input("Fecha de inicio", value=datetime.today())
hora_turno = st.sidebar.time_input("Hora primer turno", value=pd.to_datetime("06:00").time())
fecha_base = pd.to_datetime(f"{fecha_seleccionada} {hora_turno}")

# =============================================================
# 3. MOTOR DE DATOS (PRODUCCIÓN + MANTENIMIENTO)
# =============================================================
@st.cache_data
def cargar_produccion():
    return pd.read_csv('cronograma_produccion_pulp.csv')

def cargar_mantenimiento():
    # Si el usuario creó el archivo, lo lee. Si no, asume 0 horas.
    if os.path.exists('mantenimiento.csv'):
        return pd.read_csv('mantenimiento.csv')['Horas'].sum()
    return 0

try:
    df = cargar_produccion()
    horas_mantenimiento_totales = cargar_mantenimiento()
    
    df['Inicio_dt'] = fecha_base + pd.to_timedelta(df['Inicio (hs)'], unit='h')
    df['Fin_dt'] = fecha_base + pd.to_timedelta(df['Fin (hs)'], unit='h')
    df['Duracion_hs'] = df['Fin (hs)'] - df['Inicio (hs)']
    
    # Volúmenes
    df['Volumen_Lts'] = df['Tanque'].apply(lambda x: 4000 if x == 'TK-100' else 2000)
    
    # CÁLCULOS DE CAPACIDAD Y EFICIENCIA (OEE Básico)
    cantidad_equipos = df['Tanque'].nunique()
    
    # 1. Capacidad Teórica: 24/7 todo el mes
    capacidad_teorica = cantidad_equipos * 24 * dias_mes
    
    # 2. Capacidad Bruta: Turnos reales * Días laborables
    capacidad_bruta = cantidad_equipos * horas_por_turno * dias_laborables
    
    # 3. Capacidad Neta: Capacidad Bruta - Mantenimiento
    capacidad_neta = capacidad_bruta - horas_mantenimiento_totales
    
    # 4. Horas reales de producción (Makespan útil)
    horas_totales_prod = df['Duracion_hs'].sum()
    
    # 5. Capacidad Ociosa
    horas_ociosas = capacidad_neta - horas_totales_prod
    
    ocupacion_neta_pct = (horas_totales_prod / capacidad_neta) * 100

except FileNotFoundError:
    st.warning("No se encontró el archivo de planificación. Ejecutá el algoritmo MILP primero.")
    st.stop()

# =============================================================
# 4. ESTRUCTURA DE PESTAÑAS (TABS)
# =============================================================
tab_gerencia, tab_planta = st.tabs(["📊 S&OP y Eficiencia", "⚙️ Operaciones en Planta"])

# -------------------------------------------------------------
# PESTAÑA 1: VISIÓN GERENCIAL (CAPACIDAD Y VOLUMEN)
# -------------------------------------------------------------
with tab_gerencia:
    st.markdown("### Estado de Capacidad Mensual")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Capacidad Bruta", f"{capacidad_bruta} hs", help=f"Equipos * Horas Turno * Días Laborables")
    with col2:
        st.metric("Pérdidas (Mant. + Feriados)", f"-{horas_mantenimiento_totales + (dias_inactivos * cantidad_equipos * 24)} hs")
    with col3:
        st.metric("Capacidad Neta Disponible", f"{capacidad_neta} hs")
    with col4:
        delta_color = "normal" if ocupacion_neta_pct <= 85 else "inverse"
        st.metric("Saturación Neta", f"{ocupacion_neta_pct:.1f}%", 
                  delta="Riesgo de Quiebre" if ocupacion_neta_pct > 85 else "Capacidad OK", 
                  delta_color=delta_color)

    st.divider()
    
    # Gráficos gemelos: Distribución del tiempo y Volúmenes
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.markdown("**Distribución de la Capacidad Neta**")
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Producción Efectiva', 'Capacidad Ociosa'],
            values=[horas_totales_prod, horas_ociosas],
            hole=.5,
            marker_colors=['#2ca02c', '#d62728'] if horas_ociosas < 0 else ['#1f77b4', '#e377c2']
        )])
        fig_donut.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_graf2:
        st.markdown("**Litros Proyectados por Equipo**")
        df_volumen = df.groupby('Tanque')['Volumen_Lts'].sum().reset_index()
        fig_bar = px.bar(
            df_volumen, x='Tanque', y='Volumen_Lts', text_auto='.2s',
            color='Tanque', color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(height=300, showlegend=False, xaxis_title="", yaxis_title="Litros", margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------
# PESTAÑA 2: OPERACIONES EN PLANTA (GANTT)
# -------------------------------------------------------------
with tab_planta:
    st.markdown("### Cronograma de Equipos (Makespan)")
    
    fig_gantt = px.timeline(
        df, x_start="Inicio_dt", x_end="Fin_dt", y="Tanque", color="Lote",
        hover_data={"Volumen_Lts": True, "Duracion_hs": True, "Inicio (hs)": False, "Fin (hs)": False}
    )
    fig_gantt.update_yaxes(autorange="reversed")
    fig_gantt.update_layout(
        showlegend=False, height=250, margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(range=[df['Inicio_dt'].min(), df['Fin_dt'].max()], tickformat="%d/%m\n%H:%M", dtick=86400000, showgrid=True)
    )
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    st.markdown("### Hoja de Ruta Auditable")
    tabla_limpia = df[['Tanque', 'Lote', 'Volumen_Lts', 'Inicio_dt', 'Fin_dt', 'Duracion_hs']].copy()
    tabla_limpia.rename(columns={'Inicio_dt': 'Inicio', 'Fin_dt': 'Fin', 'Duracion_hs': 'Hs'}, inplace=True)
    tabla_limpia['Inicio'] = tabla_limpia['Inicio'].dt.strftime('%d/%m %H:%M')
    tabla_limpia['Fin'] = tabla_limpia['Fin'].dt.strftime('%d/%m %H:%M')
    st.dataframe(tabla_limpia, use_container_width=True, hide_index=True)