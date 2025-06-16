
StockOptimizeAI es un sistema inteligente de optimización de stock diseñado específicamente para pequeños negocios. Utiliza Inteligencia Artificial (IA) y Machine Learning (ML) para predecir la demanda futura basándose en el historial de ventas, estacionalidad y promociones.

# 🚀 StockOptimizeAI: Optimización de Inventario Inteligente para Pequeños Negocios

## 🤔 ¿Qué es StockOptimizeAI?

**StockOptimizeAI** es tu aliado estratégico para la **gestión de inventario** y la **optimización de stock** en **pequeños negocios**. Este innovador sistema aprovecha el poder de la **Inteligencia Artificial (IA)** y el **Machine Learning (ML)** para transformar la forma en que manejas tu inventario.

El objetivo es simple: ayudarte a **reducir costos** asociados con el exceso de stock y **maximizar tus ventas** asegurando que siempre tengas los productos correctos disponibles. Analiza tus **datos históricos de ventas**, considera la **estacionalidad** y el impacto de las **promociones** para **predecir la demanda futura** con alta precisión. Luego, te proporciona **recomendaciones de stock óptimas** y te alerta sobre posibles **sobre-stock o falta de stock**, permitiéndote tomar decisiones informadas y **automatizar** gran parte de tu planificación de inventario.

## ✨ Características Principales

* **Predicción de Demanda Inteligente:** Utiliza modelos de **Machine Learning** (RandomForestRegressor con Scikit-learn) para prever cuántos productos necesitarás en el futuro.
* **Recomendaciones de Stock Óptimas:** Basadas en la demanda predicha, el sistema sugiere los niveles de inventario ideales para cada producto.
* **Diagnóstico de Inventario:** Recibe alertas claras sobre situaciones de **exceso de stock** o **escasez de productos**, con explicaciones de sus implicaciones.
* **Interfaz de Usuario Intuitiva (UI/UX):** Desarrollada con **Streamlit**, ofrece una experiencia de usuario sencilla y eficaz, incluso en equipos con recursos limitados.
* **Gestión de Datos Local:** Utiliza **SQLite** como base de datos ligera para almacenar de forma persistente tus registros de ventas y optimizaciones.
* **Visualización de Datos:** Incluye gráficos de **Matplotlib** para analizar tendencias de ventas y patrones de productos a lo largo del tiempo.
* **Automatización:** Reduce la necesidad de conjeturas y cálculos manuales en tu **gestión de inventario**.

## 🛠️ Tecnologías Utilizadas

* **Python**: Lenguaje de programación principal para todo el sistema (backend ML y frontend UI).
* **Streamlit**: Framework de Python para construir interfaces de usuario web interactivas de forma rápida y ligera.
* **Scikit-learn**: Librería fundamental de Machine Learning para el entrenamiento de modelos predictivos.
* **Pandas**: Herramienta esencial para la manipulación y análisis de datos.
* **SQLite**: Base de datos relacional ligera y autónoma, ideal para almacenar los datos de ventas localmente.
* **Matplotlib**: Librería para la creación de gráficos estáticos y visualizaciones de datos.

## 🚀 Cómo Empezar

Sigue estos pasos para poner en marcha **StockOptimizeAI** en tu máquina local:

1.  **Clona este repositorio:**
    ```bash
    git clone https://github.com/santiagourdaneta/StockOptimizeAI-Optimizacion-de-Inventario-Inteligente-para-Pequenos-Negocios/
    cd StockOptimizeAI-Optimizacion-de-Inventario-Inteligente-para-Pequenos-Negocios/
    ```

2.  **Crea y activa un entorno virtual (muy recomendado para aislar dependencias):**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instala las dependencias necesarias:**
    ```bash
    pip install streamlit pandas scikit-learn matplotlib
    ```
    (Puedes generar un `requirements.txt` con `pip freeze > requirements.txt` después de instalar y luego usar `pip install -r requirements.txt` en el futuro.)

4.  **Ejecuta la aplicación Streamlit:**
    ```bash
    streamlit run app.py
    ```

    Se abrirá automáticamente una nueva pestaña en tu navegador con la interfaz de **StockOptimizAeI**.

## 📊 Estructura de la Base de Datos (`stock_data.db`)

La base de datos SQLite almacena tus registros de ventas en la tabla `ventas` con la siguiente estructura:

| Columna            | Tipo    | Descripción                                             |
| :----------------- | :------ | :------------------------------------------------------ |
| `id`               | INTEGER | Identificador único de cada venta.                      |
| `fecha`            | TEXT    | Fecha de la venta (formato 'AAAA-MM-DD').               |
| `producto`         | TEXT    | Nombre del producto vendido.                            |
| `cantidad_vendida` | INTEGER | Cantidad de unidades vendidas.                          |
| `precio_unitario`  | REAL    | Precio de cada unidad (opcional).                       |
| `promocion`        | TEXT    | Nombre de la promoción aplicada (ej. '2x1', 'Ninguna'). |

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar la precisión del modelo de IA, añadir nuevas características a la interfaz, u optimizar el código para una mayor eficiencia, no dudes en:

1.  Hacer un "Fork" del repositorio.
2.  Crear una nueva rama (`git checkout -b feature/nueva-prediccion`).
3.  Realizar tus cambios y hacer "commit" (`git commit -m 'feat: Añadir soporte para promociones personalizadas'`).
4.  Hacer "push" a tu rama (`git push origin feature/nueva-prediccion`).
5.  Abrir un "Pull Request".

---

¡Espero que **StockOptimizeAI** te ayude a llevar la **gestión de inventario** de tu pequeño negocio al siguiente nivel! Si tienes alguna pregunta o encuentras algún problema, no dudes en abrir un "Issue".
