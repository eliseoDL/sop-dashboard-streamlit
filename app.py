import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard S&OP", layout="wide")

st.title("📊 Panel Táctico S&OP (Sales & Operations Planning)")
st.markdown("Herramienta interactiva para la planificación financiera y de capacidad de planta.")

if st.button("🔄 Recargar Datos"):
    st.cache_data.clear()

@st.cache_data
def load_data():
    try:
        return pd.read_csv('resultados_sop_mensual.csv')
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No se encontró el archivo. Ejecuta el Jupyter Notebook primero.")
    st.stop()
    
# Verificamos que existan las columnas financieras (por si el usuario olvidó actualizar el CSV)
if 'Ganancia_Bruta (ARS)' not in df.columns:
    st.error("Faltan las columnas financieras en el CSV. Actualizá la Celda 4 del Jupyter Notebook y volvé a correrlo.")
    st.stop()

# --- SISTEMA DE PESTAÑAS ---
tab1, tab2 = st.tabs(["📈 Visión Ejecutiva (Evolución Global)", "🗓️ Plan Operativo (Detalle Mensual)"])

# =============================================================================
# PESTAÑA 1: VISIÓN EJECUTIVA (Evolución en el tiempo)
# =============================================================================
with tab1:
    st.header("Evolución Financiera y Nivel de Servicio")
    
    # Agrupamos los datos globales por mes
    df_evo = df.groupby('Mes').agg({
        'Ingresos (ARS)': 'sum',
        'Costo_Produccion (ARS)': 'sum',
        'Ganancia_Bruta (ARS)': 'sum',
        'Demanda_Target (L)': 'sum',
        'Volumen_Asignado (L)': 'sum'
    }).reset_index()
    df_evo['Nivel de Servicio (%)'] = (df_evo['Volumen_Asignado (L)'] / df_evo['Demanda_Target (L)']) * 100
    
    # KPIs Globales (Sumatoria total)
    ganancia_total = df_evo['Ganancia_Bruta (ARS)'].sum()
    ingreso_total = df_evo['Ingresos (ARS)'].sum()
    promedio_servicio = df_evo['Nivel de Servicio (%)'].mean()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos Proyectados (ARS)", f"${ingreso_total:,.0f}")
    c2.metric("Ganancia Bruta Total (ARS)", f"${ganancia_total:,.0f}")
    c3.metric("Nivel de Servicio Promedio", f"{promedio_servicio:.1f}%")
    
    st.markdown("---")
    
    # Gráfico 1: Evolución Financiera (Ingresos vs Costos vs Ganancia)
    st.subheader("Proyección Financiera Mensual")
    fig_fin = go.Figure()
    fig_fin.add_trace(go.Bar(x=df_evo['Mes'], y=df_evo['Ingresos (ARS)'], name='Ingresos', marker_color='#2ca02c'))
    fig_fin.add_trace(go.Bar(x=df_evo['Mes'], y=df_evo['Costo_Produccion (ARS)'], name='Costos Operativos', marker_color='#d62728'))
    fig_fin.add_trace(go.Scatter(x=df_evo['Mes'], y=df_evo['Ganancia_Bruta (ARS)'], name='Ganancia Bruta', mode='lines+markers', line=dict(color='#ff7f0e', width=3)))
    
    fig_fin.update_layout(barmode='group', yaxis_title="Moneda (ARS)", legend_title_text='Métrica')
    st.plotly_chart(fig_fin, width='stretch')
    
    # Gráfico 2: Evolución del Nivel de Servicio
    st.subheader("Evolución del Cumplimiento de Demanda (Nivel de Servicio)")
    fig_serv = px.line(df_evo, x='Mes', y='Nivel de Servicio (%)', markers=True, range_y=[80, 105], color_discrete_sequence=['#1f77b4'])
    fig_serv.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="Target 100%")
    st.plotly_chart(fig_serv, width='stretch')


# =============================================================================
# PESTAÑA 2: PLAN OPERATIVO (El detalle mes a mes que ya teníamos)
# =============================================================================
with tab2:
    # --- Filtros (Se aplican solo a esta pestaña) ---
    col_filt1, col_filt2 = st.columns(2)
    meses_disponibles = sorted(df['Mes'].unique().tolist())
    mes_seleccionado = col_filt1.selectbox("Seleccionar Mes de Planificación", meses_disponibles)
    
    df_mes = df[df['Mes'] == mes_seleccionado]
    
    skus_disponibles = sorted(df_mes['SKU'].unique().tolist())
    skus_seleccionados = col_filt2.multiselect("Filtrar por SKU", skus_disponibles, default=skus_disponibles)
    
    df_filtrado = df_mes[df_mes['SKU'].isin(skus_seleccionados)]
    
    if df_filtrado.empty:
        st.warning("⚠️ Selecciona al menos un producto.")
    else:
        df_agrupado_sku = df_filtrado.groupby('SKU').agg({
            'Demanda_Target (L)': 'max',
            'Volumen_Asignado (L)': 'sum'
        }).reset_index()

        demanda_total = df_agrupado_sku['Demanda_Target (L)'].sum()
        produccion_total = df_agrupado_sku['Volumen_Asignado (L)'].sum()
        horas_totales = df_filtrado['Horas_Consumidas'].sum()
        nivel_servicio = (produccion_total / demanda_total * 100) if demanda_total > 0 else 0

        # KPIs del Mes
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Demanda {mes_seleccionado}", f"{demanda_total:,.0f} L")
        c2.metric(f"Producción {mes_seleccionado}", f"{produccion_total:,.0f} L")
        c3.metric("Horas Máquina", f"{horas_totales:,.1f} hs")
        c4.metric("Nivel de Servicio", f"{nivel_servicio:.1f}%")
        
        st.markdown("---")
        
        # Gráficos Operativos
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.subheader(f"Cumplimiento por Producto")
            fig1 = px.bar(df_agrupado_sku, x='SKU', y=['Demanda_Target (L)', 'Volumen_Asignado (L)'], barmode='group', color_discrete_sequence=['#1f77b4', '#2ca02c'])
            fig1.update_layout(legend_title_text='')
            st.plotly_chart(fig1, width='stretch')

        with col_graf2:
            st.subheader(f"Carga Operativa por Tanque")
            df_tanques = df_filtrado.groupby('Tanque_Asignado')['Horas_Consumidas'].sum().reset_index()
            fig2 = px.pie(df_tanques, names='Tanque_Asignado', values='Horas_Consumidas', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig2, width='stretch')

        # Tabla
        st.subheader(f"Master Production Schedule (MPS) - {mes_seleccionado}")
        st.dataframe(df_filtrado, width='stretch')