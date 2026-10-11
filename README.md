# 📊 Simulador Táctico S&OP: Optimización MILP para Planificación de la Producción

## 📌 Sobre el Proyecto
Esta aplicación es una herramienta táctica de apoyo a la toma de decisiones diseñada para tender un puente entre la **Planificación Comercial (Demanda)** y la **Ejecución en Planta (Capacidad)**. 

En la industria, los sistemas tradicionales calculan requerimientos (MRP) pero suelen fallar al optimizar la capacidad física real frente a escenarios de alta demanda. Este proyecto soluciona ese cuello de botella utilizando un modelo matemático de **Programación Lineal Entera Mixta (MILP)** para evaluar escenarios multi-mes, proyectar la demanda, asegurar el nivel de servicio y asignar de forma óptima el volumen a los reactores disponibles para maximizar la rentabilidad y minimizar los costos operativos.

## 🚀 Características Principales (Business Value)
1. **Forecasting y Nivel de Servicio:** Proyecta la demanda comercial basándose en históricos de ventas, aplicando factores de estacionalidad (+15%) y políticas de stock de seguridad (+5%).
2. **Cálculo de Capacidad Real:** Modela las restricciones físicas de la planta descontando paradas por mantenimiento preventivo y tiempos de limpieza (CIP) por equipo.
3. **Optimización Matemática (PuLP):** El algoritmo decide automáticamente cuántos litros de cada SKU asignar a cada tanque específico para cumplir la demanda gastando la menor cantidad de horas máquina posibles.
4. **Dashboard Gerencial:** Interfaz web interactiva que permite a la gerencia filtrar la planificación mes a mes, evaluar cuellos de botella y visualizar métricas clave (Nivel de Servicio, Horas Máquina, Producción Asignada).

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.x
* **Modelado Matemático / Optimización:** PuLP
* **Manipulación y Análisis de Datos:** Pandas
* **Visualización Dinámica:** Plotly Express
* **Frontend / Dashboarding:** Streamlit, Jupyter Notebooks

## 📂 Estructura del Proyecto
* `historial_ventas_lavandina.csv`: Histórico comercial diario (Input Demanda).
* `maestro_equipos.csv`: Capacidades y tiempos de limpieza de reactores (Input Operaciones).
* `maestro_recetas.csv`: Estructura de costos de insumos por producto (Input Finanzas).
* `mantenimiento.csv`: Plan de paradas técnicas de equipos.
* `notebook_sop.ipynb`: Cuaderno interactivo con el paso a paso del modelo S&OP, desde el forecasting hasta el motor de optimización matemática multi-mes.
* `app_sop_mensual.py`: Código fuente del panel interactivo (Dashboard).
* `resultados_sop_mensual.csv`: Output generado por el modelo optimizado, utilizado como base de datos para el dashboard.

## ⚙️ Instrucciones para Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/tu-repo-sop.git](https://github.com/tu-usuario/tu-repo-sop.git)
   cd tu-repo-sop
