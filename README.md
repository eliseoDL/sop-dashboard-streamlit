# S&OP Tactical Planner - Optimizador de Producción MILP

Este proyecto nació para resolver un problema clásico en las fábricas: la desconexión entre lo que Comercial quiere vender y lo que Planta realmente puede fabricar. 

Casi todos los sistemas (como los MRP) calculan requerimientos, pero muchas veces ignoran si los equipos tienen las horas físicas para hacerlo. Para solucionar esto, armé un simulador S&OP en Python que proyecta la demanda y usa Programación Lineal (MILP) para decidir qué producto asignar a qué reactor, buscando siempre maximizar la rentabilidad sin pasarnos de la capacidad real.

## ¿Qué hace exactamente?

*   **Proyección de demanda (Forecasting):** Agarra el historial de ventas diario y proyecta los próximos meses, sumándole un factor de crecimiento y un % de stock de seguridad.
*   **Cálculo de capacidad real:** Mira la tabla de equipos y les descuenta las horas de mantenimiento preventivo y los tiempos de limpieza (CIP) para saber con cuántas horas útiles contamos de verdad.
*   **Motor de optimización (PuLP):** El corazón del proyecto. Si la demanda es altísima y hay cuello de botella, el algoritmo elige la combinación de productos que deje más margen de ganancia. Si estamos bien de capacidad, minimiza las horas máquina para ahorrar costos operativos.
*   **Dashboard Gerencial:** El resultado no queda en una consola, sino que se exporta y se levanta en una app de Streamlit donde podés filtrar por mes y ver los KPIs rápido (nivel de servicio, horas consumidas, etc.).

## Stack Tecnológico

*   **Python:** Lenguaje base.
*   **PuLP:** Para armar y resolver el modelo matemático de optimización.
*   **Pandas:** Para toda la limpieza y cruce de datos (Ventas, Recetas, Equipos).
*   **Streamlit & Plotly Express:** Para armar la interfaz web y los gráficos.

## Cómo correrlo localmente

1. **Cloná el repo y metete en la carpeta:**
   ```bash
   git clone https://github.com/tu-usuario/tu-repo-sop.git
   cd tu-repo-sop
   ```

2. **Instalá las librerías necesarias:**
   *(Te recomiendo usar un entorno virtual)*
   ```bash
   pip install pandas pulp streamlit plotly
   ```

3. **Ejecutá el modelo matemático:**
   Abrí el archivo `notebook_sop.ipynb` en tu Jupyter (o VSCode) y corré todas las celdas. Esto va a procesar los CSV y generar un archivo nuevo llamado `resultados_sop_mensual.csv` con la asignación óptima.

4. **Levantá el dashboard:**
   En la terminal, corré este comando para abrir la app web:
   ```bash
   streamlit run app_sop_mensual.py
   ```
