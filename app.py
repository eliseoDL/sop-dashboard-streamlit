import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard S&OP", layout="wide")

st.title("📊 Simulador Táctico S&OP")
st.markdown("Herramienta de planificación financiera y operativa mensual.")

# --- Cargar Datos ---
try:
    df_sop = pd.read_csv('resultados_sop.csv')
except FileNotFoundError:
    st.error("No se encontró el archivo resultados_sop.csv. Ejecuta el modelo primero.")
    st.stop()

# --- Filtros (Sidebar) ---
st.sidebar.header("Filtros")
skus_disponibles = df_sop['SKU'].unique().tolist()
sku_seleccionados = st.sidebar.multiselect("Seleccionar SKU", skus_disponibles, default=skus_disponibles)

# Filtrar el dataframe
df_filtrado = df_sop[df_sop['SKU'].isin(sku_seleccionados)]

# --- KPIs (Tarjetas Superiores) ---
col1, col2, col3 = st.columns(3)

demanda_total = df_filtrado['Demanda_Proyectada (L)'].sum()
produccion_total = df_filtrado['Produccion_Asignada (L)'].sum()
nivel_servicio_promedio = (produccion_total / demanda_total * 100) if demanda_total > 0 else 0

with col1:
    st.metric("Demanda Total Proyectada", f"{demanda_total:,.0f} L")
with col2:
    st.metric("Producción Total Asignada", f"{produccion_total:,.0f} L")
with col3:
    st.metric("Nivel de Servicio Promedio", f"{nivel_servicio_promedio:.1f}%")

st.markdown("---")

# --- Gráficos ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Demanda vs. Producción por SKU")
    fig1 = px.bar(
        df_filtrado, 
        x='SKU', 
        y=['Demanda_Proyectada (L)', 'Produccion_Asignada (L)'], 
        barmode='group',
        labels={'value': 'Litros', 'variable': 'Métrica'},
        color_discrete_sequence=['#1f77b4', '#2ca02c']
    )
    fig1.update_layout(legend_title_text='')
    st.plotly_chart(fig1, use_container_width=True)

with col_graf2:
    st.subheader("Nivel de Servicio por SKU (%)")
    # Gráfico de barras horizontales o de medidor (gauge) simplificado
    fig2 = px.bar(
        df_filtrado, 
        y='SKU', 
        x='Nivel_Servicio (%)', 
        orientation='h',
        color='Nivel_Servicio (%)',
        color_continuous_scale='RdYlGn',
        range_x=[0, 100]
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Tabla Detallada ---
st.subheader("Detalle del Plan de Producción")
st.dataframe(df_filtrado, use_container_width=True)