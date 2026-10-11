import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard S&OP", layout="wide")

st.title("📊 Panel Táctico S&OP (Sales & Operations Planning)")
st.markdown("Herramienta interactiva para la planificación y conciliación entre Demanda y Capacidad de Planta.")

# --- 1. Cargar Datos ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv('resultados_sop_mensual.csv')
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No se encontró el archivo 'resultados_sop_mensual.csv'. Ejecuta el Jupyter Notebook primero para generarlo.")
    st.stop()

# --- 2. Filtros de Planificación (Sidebar) ---
st.sidebar.header("Filtros de Planificación")

# Filtro de Mes
meses_disponibles = sorted(df['Mes'].unique().tolist())
mes_seleccionado = st.sidebar.selectbox("Seleccionar Mes", meses_disponibles)

# Filtrar base por el mes seleccionado
df_mes = df[df['Mes'] == mes_seleccionado]

# Filtro de SKU
skus_disponibles = sorted(df_mes['SKU'].unique().tolist())
skus_seleccionados = st.sidebar.multiselect("Seleccionar SKU", skus_disponibles, default=skus_disponibles)

# Aplicar filtro final
df_filtrado = df_mes[df_mes['SKU'].isin(skus_seleccionados)]

# --- 3. KPIs Estratégicos ---
# Agrupamos por SKU para no duplicar la Demanda Target (ya que puede estar dividida en varios tanques)
df_agrupado_sku = df_filtrado.groupby('SKU').agg({
    'Demanda_Target (L)': 'max',
    'Volumen_Asignado (L)': 'sum'
}).reset_index()

demanda_total = df_agrupado_sku['Demanda_Target (L)'].sum()
produccion_total = df_agrupado_sku['Volumen_Asignado (L)'].sum()
horas_totales = df_filtrado['Horas_Consumidas'].sum()
nivel_servicio = (produccion_total / demanda_total * 100) if demanda_total > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Demanda Total (L)", f"{demanda_total:,.0f}")
col2.metric("Producción Asignada (L)", f"{produccion_total:,.0f}")
col3.metric("Horas Máquina (hs)", f"{horas_totales:,.1f}")
col4.metric("Nivel de Servicio", f"{nivel_servicio:.1f}%")

st.markdown("---")

# --- 4. Gráficos ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader(f"Cumplimiento por Producto - {mes_seleccionado}")
    fig1 = px.bar(
        df_agrupado_sku,
        x='SKU',
        y=['Demanda_Target (L)', 'Volumen_Asignado (L)'],
        barmode='group',
        labels={'value': 'Litros', 'variable': 'Métrica'},
        color_discrete_sequence=['#1f77b4', '#2ca02c']
    )
    fig1.update_layout(legend_title_text='')
    st.plotly_chart(fig1, use_container_width=True)

with col_graf2:
    st.subheader(f"Carga Operativa por Tanque - {mes_seleccionado}")
    # Agrupamos las horas por tanque
    df_tanques = df_filtrado.groupby('Tanque_Asignado')['Horas_Consumidas'].sum().reset_index()
    fig2 = px.pie(
        df_tanques,
        names='Tanque_Asignado',
        values='Horas_Consumidas',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- 5. Tabla de Master Production Schedule (MPS) ---
st.subheader("Detalle Táctico de Asignación")
st.dataframe(df_filtrado, use_container_width=True)