import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import sqlite3
import os

# --- 1. Configuración Inicial de Streamlit ---
st.set_page_config(layout="centered", page_title="Optimizador de Stock Inteligente")
st.title("📦 Sistema de Optimización de Stock para Pequeños Negocios")
st.markdown("Tu **cerebro mágico** para el inventario: ¡predice la demanda y recomienda el stock óptimo!")
st.write("---")

# --- 2. Configuración y Funciones de la Base de Datos SQLite ---
DB_NAME = 'stock_data.db'

def init_db():
    """Inicializa la base de datos y crea la tabla de ventas si no existe."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad_vendida INTEGER NOT NULL,
            precio_unitario REAL,
            promocion TEXT,
            UNIQUE(fecha, producto)
        )
    ''')
    conn.commit()
    conn.close()

def add_venta(fecha, producto, cantidad, precio=0.0, promocion=''):
    """Añade un registro de venta a la base de datos o lo actualiza si ya existe."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO ventas (fecha, producto, cantidad_vendida, precio_unitario, promocion)
            VALUES (?, ?, ?, ?, ?)
        ''', (fecha, producto, cantidad, precio, promocion))
        conn.commit()
        return True, f"Venta de {cantidad} de {producto} en {fecha} registrada."
    except sqlite3.IntegrityError:
        c.execute('''
            UPDATE ventas
            SET cantidad_vendida = ?, precio_unitario = ?, promocion = ?
            WHERE fecha = ? AND producto = ?
        ''', (cantidad, precio, promocion, fecha, producto))
        conn.commit()
        return True, f"Venta de {producto} en {fecha} actualizada."
    except Exception as e:
        return False, f"Error al añadir/actualizar venta: {e}"
    finally:
        conn.close()

@st.cache_data
def get_all_ventas():
    """Obtiene todas las ventas de la base de datos como un DataFrame de Pandas."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM ventas ORDER BY fecha ASC", conn)
    conn.close()
    return df

# --- 3. Funciones del Cerebro Inteligente (Modelo de Predicción ML) ---

def train_model(df_ventas):
    """
    Entrena un modelo de Machine Learning para predecir la cantidad de ventas.
    Retorna los modelos entrenados y los encoders.
    """
    if df_ventas.empty:
        return None, None, None, "No hay datos de ventas suficientes para entrenar el modelo. ¡Registra más ventas!"

    df_ventas_copy = df_ventas.copy()
    df_ventas_copy['fecha'] = pd.to_datetime(df_ventas_copy['fecha'])

    df_ventas_copy['dia_semana'] = df_ventas_copy['fecha'].dt.dayofweek
    df_ventas_copy['mes'] = df_ventas_copy['fecha'].dt.month
    df_ventas_copy['dia_del_mes'] = df_ventas_copy['fecha'].dt.day
    df_ventas_copy['anio'] = df_ventas_copy['fecha'].dt.year

    encoder_producto = LabelEncoder()
    encoder_promocion = LabelEncoder()

    df_ventas_copy['producto_encoded'] = encoder_producto.fit_transform(df_ventas_copy['producto'])
    df_ventas_copy['promocion'] = df_ventas_copy['promocion'].fillna('Ninguna')
    df_ventas_copy['promocion_encoded'] = encoder_promocion.fit_transform(df_ventas_copy['promocion'])

    features = ['dia_semana', 'mes', 'dia_del_mes', 'anio', 'producto_encoded', 'promocion_encoded']
    target = 'cantidad_vendida'

    models = {}
    for producto_id in df_ventas_copy['producto_encoded'].unique():
        df_producto = df_ventas_copy[df_ventas_copy['producto_encoded'] == producto_id]
        if len(df_producto) >= 5:
            model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            model.fit(df_producto[features], df_producto[target])
            models[producto_id] = model
        else:
            pass

    if not models:
        return None, None, None, "No se pudieron entrenar modelos para ningún producto. Asegúrate de tener al menos 5 registros de venta por producto."

    return models, encoder_producto, encoder_promocion, "Modelos entrenados con éxito."

# --- Función de Carga y Entrenamiento Cacheada (DEBE ESTAR DEFINIDA DESPUÉS DE train_model) ---
@st.cache_resource
def load_models_and_encoders():
    df_ventas_cache = get_all_ventas()
    if not df_ventas_cache.empty:
        models, encoder_producto, encoder_promocion, status_msg = train_model(df_ventas_cache)
        return models, encoder_producto, encoder_promocion, status_msg
    return None, None, None, "No hay datos para entrenar modelos."


def predict_demand(models, encoder_producto, encoder_promocion, producto_nombre, fecha_prediccion, promocion_futura=''):
    """
    Predice la demanda de un producto para una fecha futura utilizando los modelos entrenados.
    """
    if models is None or encoder_producto is None or encoder_promocion is None:
        return 0, "Error: Modelos no disponibles. Revisa si hay suficientes datos de entrenamiento."

    try:
        producto_encoded = encoder_producto.transform([producto_nombre])[0]
    except ValueError:
        return 0, f"Producto '{producto_nombre}' no ha sido visto en el historial de ventas. No se puede predecir."

    if producto_encoded not in models:
        return 0, f"No hay suficiente historial de ventas para '{producto_nombre}' para una predicción fiable (mínimo 5 registros)."

    model = models[producto_encoded]

    fecha_dt = pd.to_datetime(fecha_prediccion)
    dia_semana = fecha_dt.dayofweek
    mes = fecha_dt.month
    dia_del_mes = fecha_dt.day
    anio = fecha_dt.year

    promocion_encoded = 0
    if promocion_futura in encoder_promocion.classes_:
        promocion_encoded = encoder_promocion.transform([promocion_futura])[0]
    else:
        if 'Ninguna' in encoder_promocion.classes_:
            promocion_encoded = encoder_promocion.transform(['Ninguna'])[0]

    input_data = pd.DataFrame([[dia_semana, mes, dia_del_mes, anio, producto_encoded, promocion_encoded]],
                              columns=['dia_semana', 'mes', 'dia_del_mes', 'anio', 'producto_encoded', 'promocion_encoded'])

    prediccion = model.predict(input_data)[0]
    return max(0, int(round(prediccion))), "Predicción de demanda generada."

def calculate_optimal_stock(predicted_demand, current_stock, safety_stock_factor=0.25):
    """
    Calcula el nivel de stock óptimo y ofrece un diagnóstico de sobre-stock o falta de stock.
    """
    safety_stock = predicted_demand * safety_stock_factor
    recommended_stock = int(round(predicted_demand + safety_stock))

    diagnosis = ""
    if current_stock < (predicted_demand + safety_stock) * 0.80:
        diagnosis = "Riesgo de **falta de stock** 📉. Podrías perder ventas o tener clientes insatisfechos. ¡Considera reabastecer!"
    elif current_stock > (predicted_demand + safety_stock) * 1.50:
        diagnosis = "Riesgo de **sobre-stock** 📈. Esto podría generar costos de almacenamiento, productos obsoletos o capital inmovilizado."
    else:
        diagnosis = "Nivel de stock **aceptable** ✅. ¡Estás en un buen punto!"

    return recommended_stock, diagnosis

# --- 4. INICIALIZACIÓN DE LA APLICACIÓN PRINCIPAL ---
# Este bloque de código se ejecuta una vez al inicio.
init_db() # Asegura que la DB exista al inicio de la ejecución de la app

# Llamada a la función de carga/entrenamiento DEPUÉS de que todas las funciones anteriores
# (DB y ML) hayan sido definidas.
with st.spinner('Cargando y entrenando los modelos de IA... Esto puede tardar un momento si tienes muchos datos.'):
    models, encoder_producto, encoder_promocion, model_status_msg = load_models_and_encoders()
    if models is None:
        st.warning(model_status_msg) # Mostrar mensaje si no se pudo entrenar

# --- 5. Lógica de la Interfaz de Usuario (UI) ---
# Esta es la parte interactiva de Streamlit que se re-ejecuta.
st.sidebar.header("Menú 📊")
page = st.sidebar.radio("Navegación", ["✍️ Registrar Venta", "📈 Optimizar Stock", "📚 Ver Historial"])

# --- Sección: Registrar Venta ---
if page == "✍️ Registrar Venta":
    st.header("✍️ Registrar una Nueva Venta")
    st.write("Añade tus ventas diarias aquí para que el sistema aprenda y mejore sus predicciones.")

    with st.form("form_add_venta"):
        venta_fecha = st.date_input("Fecha de Venta:", datetime.today().date(), help="Selecciona la fecha en que ocurrió la venta.")
        
        productos_existentes = get_all_ventas()['producto'].unique().tolist() if not get_all_ventas().empty else []
        
        producto_opcion_raw = st.selectbox("Producto:", 
                                         ["- Nuevo Producto -"] + sorted(productos_existentes),
                                         help="Selecciona un producto existente o elige '- Nuevo Producto -' para ingresar uno nuevo.",
                                         key="producto_opcion_select")
        
        venta_producto = ""
        if producto_opcion_raw == "- Nuevo Producto -":
            venta_producto = st.text_input("Nombre del Nuevo Producto:", help="Ingresa el nombre del nuevo producto (ej. 'Caramelos de Menta').", key="new_product_input")
        else:
            venta_producto = producto_opcion_raw

        venta_cantidad = st.number_input("Cantidad Vendida:", min_value=1, value=1, step=1, help="Ingresa la cantidad de unidades vendidas.")
        venta_precio = st.number_input("Precio Unitario (opcional, para tus registros):", min_value=0.0, value=0.0, step=0.01, help="Ingresa el precio por unidad vendida. Puede ser 0.0 si no es relevante para el stock.")
        venta_promocion = st.text_input("Promoción Aplicada (ej. '2x1', 'Navidad', 'Ninguna'):", "Ninguna", help="Indica si hubo alguna promoción que afectara esta venta.")

        submitted = st.form_submit_button("💾 Guardar Venta")
        if submitted:
            if not venta_producto or venta_producto.strip() == "":
                st.error("❌ Error: Por favor, ingresa o selecciona un nombre de producto válido.")
            elif venta_cantidad <= 0:
                st.error("❌ Error: La cantidad vendida debe ser un número positivo.")
            elif venta_precio < 0:
                st.error("❌ Error: El precio unitario no puede ser negativo.")
            else:
                success, msg = add_venta(str(venta_fecha), venta_producto.strip(), venta_cantidad, venta_precio, venta_promocion.strip())
                if success:
                    st.success(f"✅ ¡{msg}!")
                    get_all_ventas.clear()
                    load_models_and_encoders.clear() 
                    st.rerun()
                else:
                    st.error(f"❌ Error al registrar venta: {msg}")

# --- Sección: Optimizar Stock ---
elif page == "📈 Optimizar Stock":
    st.header("📊 Optimizar Nivel de Stock")
    st.write("Predice la demanda futura y recibe recomendaciones de stock para tus productos.")

    df_ventas_actual = get_all_ventas()

    if df_ventas_actual.empty:
        st.warning("⚠️ No hay datos de ventas registrados. Por favor, registra algunas ventas primero para poder optimizar.")
    elif models is None:
        st.warning("⚠️ No hay suficientes datos para entrenar el modelo (mínimo 5 ventas por producto). Registra más ventas o espera a que haya variedad de fechas/productos.")
    else:
        productos_para_optimizar = sorted(df_ventas_actual['producto'].unique().tolist())
        
        st.subheader("Selecciona Producto y Parámetros de Predicción")
        selected_product_opt = st.selectbox("Producto:", productos_para_optimizar, key="product_opt",
                                            help="Elige el producto para el cual quieres optimizar el stock.")
        
        default_pred_date = datetime.today().date() + timedelta(days=7)
        prediction_date_opt = st.date_input("Fecha para la cual quieres la predicción:", default_pred_date, key="date_opt",
                                            help="Selecciona la fecha futura para la cual el sistema debe predecir la demanda.")

        current_stock_opt = st.number_input(f"Stock actual de '{selected_product_opt}':", min_value=0, value=0, step=1, key="stock_opt",
                                            help="Ingresa la cantidad actual de este producto en tu inventario.")
        promocion_futura_opt = st.text_input(f"¿Habrá promoción para '{selected_product_opt}' en la fecha de predicción? (ej. 'Oferta Verano', 'Ninguna')", "Ninguna", key="promo_opt",
                                             help="Si sabes de una promoción futura, inclúyela para una predicción más precisa.")

        if st.button("✨ Calcular Stock Óptimo"):
            with st.spinner('Analizando y prediciendo la demanda...'):
                predicted_demand, msg_pred = predict_demand(models, encoder_producto, encoder_promocion, 
                                                               selected_product_opt, prediction_date_opt, promocion_futura_opt)
                
                if predicted_demand > 0:
                    st.subheader(f"🔮 Predicción de Demanda para {selected_product_opt} el {prediction_date_opt}:")
                    st.success(f"La demanda esperada es de **{predicted_demand} unidades**.")
                    st.info(f"Mensaje de la predicción: {msg_pred}") 

                    recommended_stock, diagnosis_msg = calculate_optimal_stock(predicted_demand, current_stock_opt)
                    st.subheader("💡 Recomendación y Diagnóstico de Stock:")
                    st.write(f"Stock actual: **{current_stock_opt} unidades**.")
                    st.write(f"Stock recomendado: **{recommended_stock} unidades** (incluye margen de seguridad).")
                    st.markdown(f"**Diagnóstico:** {diagnosis_msg}")
                else:
                    st.warning(f"❌ No se pudo predecir la demanda para '{selected_product_opt}'. {msg_pred}")
                    st.info("Asegúrate de tener suficientes datos históricos para este producto (al menos 5 registros con variedad de fechas y promociones).")

# --- Sección: Ver Historial ---
elif page == "📚 Ver Historial":
    st.header("📚 Historial de Ventas y Tendencias")
    st.write("Explora tus ventas pasadas y visualiza patrones importantes.")

    df_historial = get_all_ventas()

    if df_historial.empty:
        st.info("ℹ️ Aún no hay ventas registradas en el historial. ¡Registra tus ventas para ver los datos aquí!")
    else:
        st.subheader("Todas las Ventas Registradas:")
        st.dataframe(df_historial, use_container_width=True)

        st.subheader("📈 Análisis Visual de Ventas:")

        product_sales = df_historial.groupby('producto')['cantidad_vendida'].sum().sort_values(ascending=False)
        if not product_sales.empty:
            st.write("#### Porcentaje de Ventas por Producto:")
            fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
            ax_pie.pie(product_sales, labels=product_sales.index, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
            ax_pie.axis('equal')
            ax_pie.set_title('Distribución de Ventas por Producto')
            st.pyplot(fig_pie)
        else:
            st.info("No hay suficientes datos para generar el gráfico de pastel.")

        daily_sales = df_historial.groupby('fecha')['cantidad_vendida'].sum().reset_index()
        daily_sales['fecha'] = pd.to_datetime(daily_sales['fecha'])
        daily_sales = daily_sales.sort_values('fecha')

        if not daily_sales.empty and len(daily_sales) > 1:
            st.write("#### Tendencia de Ventas Totales por Día:")
            fig_line, ax_line = plt.subplots(figsize=(10, 6))
            ax_line.plot(daily_sales['fecha'], daily_sales['cantidad_vendida'], marker='o', linestyle='-', color='blue')
            ax_line.set_title('Ventas Totales por Día')
            ax_line.set_xlabel('Fecha')
            ax_line.set_ylabel('Cantidad Vendida')
            ax_line.grid(True, linestyle='--', alpha=0.7)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_line)
        else:
            st.info("No hay suficientes datos o puntos de fecha para generar la tendencia de ventas diaria.")

        productos_para_graficar = sorted(df_historial['producto'].unique().tolist())
        if productos_para_graficar:
            st.write("#### Tendencia de Ventas Individual por Producto:")
            selected_product_chart = st.selectbox("Selecciona un producto para ver su tendencia individual:", 
                                                  productos_para_graficar, key="product_chart_select")
            df_product_trend = df_historial[df_historial['producto'] == selected_product_chart].groupby('fecha')['cantidad_vendida'].sum().reset_index()
            df_product_trend['fecha'] = pd.to_datetime(df_product_trend['fecha'])
            df_product_trend = df_product_trend.sort_values('fecha')

            if not df_product_trend.empty and len(df_product_trend) > 1:
                fig_prod_line, ax_prod_line = plt.subplots(figsize=(10, 6))
                ax_prod_line.plot(df_product_trend['fecha'], df_product_trend['cantidad_vendida'], marker='o', linestyle='-', color='purple')
                ax_prod_line.set_title(f'Ventas de {selected_product_chart} por Día')
                ax_prod_line.set_xlabel('Fecha')
                ax_prod_line.set_ylabel('Cantidad Vendida')
                ax_prod_line.grid(True, linestyle='--', alpha=0.7)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig_prod_line)
            else:
                st.info(f"No hay suficientes datos o puntos de fecha para generar la tendencia de ventas para '{selected_product_chart}'.")
        else:
            st.info("No hay productos disponibles para graficar sus tendencias individuales.")

st.write("---")
st.markdown("Desarrollado con ❤️ por Santiago Urdaneta (Python, Streamlit, Scikit-learn, SQLite).")