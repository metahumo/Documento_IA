# Ejercicio de Regresión Lineal - Housing Dataset
# Análisis y predicción de precios de viviendas usando regresión lineal

import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

# ==========================================
# 1. CARGA Y EXPLORACIÓN INICIAL DE DATOS
# ==========================================

print("=" * 50)
print("1. CARGA Y EXPLORACIÓN INICIAL DE DATOS")
print("=" * 50)

# Cargar los datos
datos = pd.read_csv("housing.csv")

# Primeras filas del dataset
print("\nPrimeras filas del dataset:")
print(datos.head())

# Conteo de valores de proximidad al océano
print("\nDistribución de ocean_proximity:")
print(datos["ocean_proximity"].value_counts())

# Información general del dataset
print("\nInformación del dataset:")
datos.info()

# Estadísticas descriptivas
print("\nEstadísticas descriptivas:")
print(datos.describe())

# Histogramas de las variables
print("\nGenerando histogramas...")
datos.hist(figsize=(15, 8), bins=30, edgecolor="black")
plt.tight_layout()
plt.savefig("histogramas.png")
print("Histogramas guardados en 'histogramas.png'")
plt.close()

# ==========================================
# 2. VISUALIZACIÓN GEOGRÁFICA
# ==========================================

print("\n" + "=" * 50)
print("2. VISUALIZACIÓN GEOGRÁFICA")
print("=" * 50)

# Gráfico de dispersión geográfica con información de precio y población
print("\nGenerando visualización geográfica...")
plt.figure(figsize=(12, 8))
sb.scatterplot(x="latitude", y="longitude", data=datos, hue="median_house_value", 
               palette="coolwarm", size="population", sizes=(10, 300))
plt.title("Distribución Geográfica de Viviendas")
plt.savefig("distribucion_geografica.png")
print("Visualización guardada en 'distribucion_geografica.png'")
plt.close()

# Análisis de casos con ingreso mediano alto
print("\nVisualizando casos con ingreso mediano > 14...")
plt.figure(figsize=(12, 8))
sb.scatterplot(x="latitude", y="longitude", data=datos[datos.median_income > 14], 
               hue="median_house_value", palette="coolwarm")
plt.title("Viviendas con Ingreso Mediano Alto")
plt.savefig("ingresos_altos.png")
print("Visualización guardada en 'ingresos_altos.png'")
plt.close()

# ==========================================
# 3. LIMPIEZA DE DATOS
# ==========================================

print("\n" + "=" * 50)
print("3. LIMPIEZA DE DATOS")
print("=" * 50)

# Eliminar valores nulos
print("\nEliminando valores nulos...")
datos_na = datos.dropna()
print("Información después de eliminar valores nulos:")
datos_na.info()

# ==========================================
# 4. CODIFICACIÓN DE VARIABLES CATEGÓRICAS
# ==========================================

print("\n" + "=" * 50)
print("4. CODIFICACIÓN DE VARIABLES CATEGÓRICAS")
print("=" * 50)

# Mostrar la variable categórica
print("\nVariable categórica 'ocean_proximity':")
print(datos_na["ocean_proximity"].value_counts())

# Crear variables dummy (One-Hot Encoding)
print("\nAplicando One-Hot Encoding...")
dummies = pd.get_dummies(datos_na["ocean_proximity"], dtype=int)
datos_na = datos_na.join(dummies)

# Eliminar la columna original
datos_na = datos_na.drop(["ocean_proximity"], axis=1)

print("\nPrimeras filas después de la codificación:")
print(datos_na.head())

# ==========================================
# 5. ANÁLISIS DE CORRELACIONES
# ==========================================

print("\n" + "=" * 50)
print("5. ANÁLISIS DE CORRELACIONES")
print("=" * 50)

# Matriz de correlación
print("\nMatriz de correlación:")
print(datos_na.corr())

# Heatmap de correlaciones
print("\nGenerando heatmap de correlaciones...")
plt.figure(figsize=(15, 8))
sb.set(rc={'figure.figsize': (15, 8)})
sb.heatmap(datos_na.corr(), annot=True, cmap="YlGnBu")
plt.title("Matriz de Correlación")
plt.tight_layout()
plt.savefig("correlaciones.png")
print("Heatmap guardado en 'correlaciones.png'")
plt.close()

# Correlaciones con median_house_value
print("\nCorrelaciones con median_house_value (ordenadas):")
print(datos_na.corr()["median_house_value"].sort_values(ascending=False))

# Gráfico de dispersión: precio vs ingreso mediano
print("\nGenerando gráfico de dispersión precio vs ingreso...")
plt.figure(figsize=(10, 6))
sb.scatterplot(x=datos_na["median_house_value"], y=datos_na["median_income"])
plt.title("Precio de Vivienda vs Ingreso Mediano")
plt.savefig("precio_vs_ingreso.png")
print("Gráfico guardado en 'precio_vs_ingreso.png'")
plt.close()

# ==========================================
# 6. INGENIERÍA DE CARACTERÍSTICAS
# ==========================================

print("\n" + "=" * 50)
print("6. INGENIERÍA DE CARACTERÍSTICAS")
print("=" * 50)

# Crear nueva característica: proporción de habitaciones
print("\nCreando nueva característica 'bedroom_ratio'...")
datos_na["bedroom_ratio"] = datos_na["total_bedrooms"] / datos_na["total_rooms"]

# Nuevo heatmap con la característica adicional
print("\nGenerando nuevo heatmap con bedroom_ratio...")
plt.figure(figsize=(15, 8))
sb.heatmap(datos_na.corr(), annot=True, cmap="YlGnBu")
plt.title("Matriz de Correlación (con bedroom_ratio)")
plt.tight_layout()
plt.savefig("correlaciones_con_bedroom_ratio.png")
print("Heatmap guardado en 'correlaciones_con_bedroom_ratio.png'")
plt.close()

# ==========================================
# 7. PREPARACIÓN DE DATOS PARA EL MODELO
# ==========================================

print("\n" + "=" * 50)
print("7. PREPARACIÓN DE DATOS PARA EL MODELO")
print("=" * 50)

# Separar características (X) y etiqueta (y)
print("\nSeparando características y etiqueta...")
X = datos_na.drop(["median_house_value"], axis=1)
y = datos_na["median_house_value"]

# Dividir en conjuntos de entrenamiento y prueba
print("Dividiendo datos en entrenamiento (80%) y prueba (20%)...")
X_ent, X_pru, y_ent, y_pru = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Tamaño del conjunto de entrenamiento: {len(X_ent)}")
print(f"Tamaño del conjunto de prueba: {len(X_pru)}")

# ==========================================
# 8. ENTRENAMIENTO DEL MODELO (SIN ESCALAR)
# ==========================================

print("\n" + "=" * 50)
print("8. ENTRENAMIENTO DEL MODELO (SIN ESCALAR)")
print("=" * 50)

# Crear y entrenar el modelo
print("\nCreando modelo de regresión lineal...")
modelo = LinearRegression()

print("Entrenando modelo...")
modelo.fit(X_ent, y_ent)

# Realizar predicciones
print("Realizando predicciones...")
predicciones = modelo.predict(X_pru)

# Comparativa de predicciones vs valores reales
print("\nComparativa de primeras 10 predicciones:")
comparativa = pd.DataFrame({
    "Prediccion": predicciones[:10], 
    "Valor Real": y_pru.values[:10]
})
print(comparativa)

# Evaluación del modelo
print("\n--- EVALUACIÓN DEL MODELO (SIN ESCALAR) ---")
print(f"Score en entrenamiento: {modelo.score(X_ent, y_ent):.4f}")
print(f"Score en prueba: {modelo.score(X_pru, y_pru):.4f}")

# Calcular el error
mse = mean_squared_error(y_pru, predicciones)
rmse = np.sqrt(mse)

print(f"\nMean Squared Error (MSE): {mse:,.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:,.2f}")

# ==========================================
# 9. ESCALAMIENTO DE CARACTERÍSTICAS
# ==========================================

print("\n" + "=" * 50)
print("9. ESCALAMIENTO DE CARACTERÍSTICAS")
print("=" * 50)

print("\nEstadísticas antes del escalamiento:")
print(datos_na.describe())

# Aplicar StandardScaler
print("\nAplicando StandardScaler...")
scaler = StandardScaler()

X_ent_esc = scaler.fit_transform(X_ent)
X_pru_esc = scaler.transform(X_pru)

print("\nPrimeras filas del conjunto de entrenamiento sin escalar:")
print(X_ent.head())

print("\nPrimeras filas del conjunto de entrenamiento escalado:")
print(pd.DataFrame(X_ent_esc, columns=X_ent.columns).head())

# ==========================================
# 10. ENTRENAMIENTO DEL MODELO (CON ESCALAR)
# ==========================================

print("\n" + "=" * 50)
print("10. ENTRENAMIENTO DEL MODELO (CON DATOS ESCALADOS)")
print("=" * 50)

# Crear y entrenar nuevo modelo con datos escalados
print("\nCreando nuevo modelo con datos escalados...")
modelo_escalado = LinearRegression()

print("Entrenando modelo con datos escalados...")
modelo_escalado.fit(X_ent_esc, y_ent)

# Realizar predicciones
print("Realizando predicciones con datos escalados...")
predicciones_esc = modelo_escalado.predict(X_pru_esc)

# Evaluación del modelo escalado
print("\n--- EVALUACIÓN DEL MODELO (CON ESCALAR) ---")
print(f"Score en entrenamiento: {modelo_escalado.score(X_ent_esc, y_ent):.4f}")
print(f"Score en prueba: {modelo_escalado.score(X_pru_esc, y_pru):.4f}")

# Calcular el error con datos escalados
mse_esc = mean_squared_error(y_pru, predicciones_esc)
rmse_esc = np.sqrt(mse_esc)

print(f"\nMean Squared Error (MSE): {mse_esc:,.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse_esc:,.2f}")

# ==========================================
# 11. COMPARACIÓN DE RESULTADOS
# ==========================================

print("\n" + "=" * 50)
print("11. COMPARACIÓN DE RESULTADOS")
print("=" * 50)

print("\n--- RESUMEN COMPARATIVO ---")
print("\nModelo SIN escalar:")
print(f"  R² Entrenamiento: {modelo.score(X_ent, y_ent):.4f}")
print(f"  R² Prueba: {modelo.score(X_pru, y_pru):.4f}")
print(f"  RMSE: {rmse:,.2f}")

print("\nModelo CON escalar:")
print(f"  R² Entrenamiento: {modelo_escalado.score(X_ent_esc, y_ent):.4f}")
print(f"  R² Prueba: {modelo_escalado.score(X_pru_esc, y_pru):.4f}")
print(f"  RMSE: {rmse_esc:,.2f}")

print("\n" + "=" * 50)
print("ANÁLISIS COMPLETADO")
print("=" * 50)
