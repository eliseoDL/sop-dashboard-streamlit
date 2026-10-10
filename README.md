📊 S&OP y Optimización Táctica: Simulador MILP para Planta

Sobre el Proyecto

Esta aplicación es una herramienta de apoyo a la toma de decisiones diseñada para tender un puente entre la Planificación Comercial/Demanda y la Ejecución en Planta.

En la industria, especialmente en estructuras PyME, los sistemas ERP (como SAP o sistemas locales) calculan los requerimientos de materiales (MRP), pero fallan al momento de optimizar la capacidad física de los equipos. Este proyecto soluciona esa desconexión utilizando un modelo matemático de Programación Lineal Entera Mixta (MILP) con la librería PuLP.

En lugar de solo secuenciar lotes operativos, el modelo cruza pronósticos de ventas con la capacidad real de los reactores y los costos de formulación, generando un plan táctico que maximiza la rentabilidad mensual y garantiza el nivel de servicio.

Inputs del Modelo

Para lograr una visión integral del negocio, el simulador se alimenta de:

Historial de Ventas: Para proyectar la demanda mensual.

Recetas y Costos (BOM): Explosión de materiales para calcular el costo por litro fabricado y márgenes.

Capacidad y Mantenimiento: Tiempos de limpieza (CIP) y paradas de mantenimiento reales de los reactores para determinar la capacidad técnica factible.

Tecnologías Utilizadas

Lenguaje: Python

Optimización Matemática: PuLP

Manipulación de Datos: Pandas

Visualización: Plotly Express

Frontend / Deployment: Streamlit

Instrucciones para Ejecución Local

Clonar el repositorio:

git clone https://github.com/tu-usuario/tu-repo.git


Instalar dependencias:

pip install -r requirements.txt


Ejecutar el Dashboard:

streamlit run app_sop.py

