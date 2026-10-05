# 🏭 S&OP y Optimización de Planta: Secuenciación MILP para Reactores

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)
![PuLP](https://img.shields.io/badge/PuLP-Optimization-green.svg)

##  Sobre el Proyecto
Esta aplicación es una herramienta de apoyo a la toma de decisiones diseñada para tender un puente entre la **Planificación Comercial/Demanda ** y la **Ejecución en Planta**. 

En la industria, especialmente en estructuras PyME, los sistemas ERP (como SAP o sistemas locales) calculan los requerimientos de materiales (MRP), pero fallan al momento de optimizar la capacidad física de los equipos. Este proyecto soluciona ese cuello de botella utilizando un modelo matemático de **Programación Lineal Entera Mixta (MILP) utilizando la libreria pulp** para secuenciar lotes de producción (lavandinas y productos de limpieza) en múltiples reactores, garantizando el menor tiempo operativo posible (*Makespan*).

## Características Principales
- **Motor Matemático (PuLP):** Asignación óptima de lotes a tanques (TK-100, TK-200) evitando superposiciones y minimizando tiempos muertos.
- **Análisis de Capacidad:** Cálculo en tiempo real del porcentaje de ocupación de la planta según el esquema de turnos (1, 2 o 3 turnos).
- **Gantt Interactivo (Plotly):** Visualización dinámica del Master Production Schedule (MPS) permitiendo a los supervisores auditar los cortes exactos de cada lote.
- **Interfaz Web (Streamlit):** Panel de control amigable que permite ajustar fechas, horarios de inicio y parámetros operativos sin tocar una sola línea de código.

## Tecnologías Utilizadas
- **Lenguaje:** Python
- **Optimización Matemática:** PuLP
- **Manipulación de Datos:** Pandas
- **Visualización:** Plotly Express
- **Frontend / Deployment:** Streamlit

## Instrucciones para Ejecución Local

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/tu-usuario/tu-repo.git](https://github.com/tu-usuario/tu-repo.git)
