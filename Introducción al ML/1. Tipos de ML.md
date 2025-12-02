
---

# Tipos de Aprendizaje Automático

En este documento presentamos los tres enfoques principales del *machine learning*: **aprendizaje supervisado**, **no supervisado** y **aprendizaje por refuerzo**. Primero veremos su funcionamiento general, después mostraremos un ejemplo práctico para cada uno y, finalmente, un ejemplo orientado a ciberseguridad. Cerramos con un apartado de **conceptos clave** para asentar la terminología fundamental.

---

## 1. Aprendizaje Supervisado

En el aprendizaje supervisado entrenamos modelos utilizando datos que ya incluyen la respuesta correcta. Es decir, disponemos de pares **(entrada, etiqueta)** y el objetivo del modelo es aprender a predecir la etiqueta adecuada para nuevas entradas.

### Ejemplo práctico general
Imaginemos que queremos predecir el precio de viviendas. Disponemos de un dataset con características como metros cuadrados, número de habitaciones y localización, junto con el precio real de venta. Entrenamos un modelo para que aprenda la relación entre estas variables y el precio final.

### Ejemplo en ciberseguridad
Un caso muy común es la **detección de malware**. Disponemos de un conjunto de muestras etiquetadas como “malicioso” o “benigno”. Entrenamos un clasificador para que, ante un nuevo binario, estime si es malware basándose en características como llamadas al sistema, permisos o patrones de comportamiento.

---

## 2. Aprendizaje No Supervisado

En este enfoque no tenemos etiquetas. El modelo debe descubrir la estructura interna de los datos, agrupando elementos similares o encontrando patrones ocultos.

### Ejemplo práctico general
Supongamos que analizamos miles de perfiles de clientes sin etiquetas. Aplicamos un algoritmo de *clustering* para agruparlos según patrones de compra, de manera que podamos identificar segmentos naturales como “clientes que compran productos de alto valor” o “compradores esporádicos”.

### Ejemplo en ciberseguridad
En monitorización de red, podemos utilizar *clustering* para detectar comportamientos atípicos. Si un host comienza a generar tráfico muy diferente al de su grupo natural, lo consideramos una **anomalía**, lo cual puede indicar una intrusión, escaneo lateral o exfiltración.

---

## 3. Aprendizaje por Refuerzo

En el aprendizaje por refuerzo existe un **agente** que interactúa con un entorno. El agente toma acciones, observa el resultado y recibe una recompensa. A partir de esa retroalimentación aprende una política que maximiza la recompensa acumulada.

### Ejemplo práctico general
Podemos entrenar un agente para jugar a un videojuego. El entorno es el propio juego, las acciones son los movimientos, y la recompensa puede ser la puntuación obtenida. Con el tiempo, el agente aprenderá a maximizar el score.

### Ejemplo en ciberseguridad
Un uso avanzado consiste en entrenar un agente para **automatizar tareas de defensa**. Por ejemplo, aprender a ajustar reglas de firewall o priorizar alertas de un SOC según el histórico de aciertos. El agente recibe recompensas cuando una decisión reduce incidentes o bloquea actividades sospechosas.

---

# Conceptos Clave

A continuación presentamos una lista de conceptos fundamentales que aparecen en los tres tipos de aprendizaje.

### • Regresión
Técnica supervisada donde queremos predecir un valor numérico continuo. Ejemplo: estimar el precio de una casa o el tiempo de respuesta de un servidor.

### • Clasificación
Tarea supervisada en la que asignamos una etiqueta discreta a cada muestra. Ejemplo: “malware vs. benigno”, “intrusión vs. normal”.

### • Clustering
Método no supervisado que agrupa elementos por similitud sin usar etiquetas. Es útil para segmentación de usuarios o detección de anomalías.

### • Agente
En aprendizaje por refuerzo, es la entidad que toma decisiones dentro de un entorno. Selecciona acciones basadas en una política que trata de maximizar la recompensa.

### • Recompensa
Señal numérica que indica al agente si su acción ha sido buena o mala. Es la base del aprendizaje en refuerzo.

### • Política
Estrategia que define qué acción tomar en cada estado del entorno. El objetivo del entrenamiento es mejorar esta política.

### • Características (*features*)
Atributos o variables que describen cada muestra. Pueden ser numéricas, categóricas o derivadas. Su selección es clave para el rendimiento del modelo.

### • Overfitting
Cuando un modelo aprende demasiado los datos de entrenamiento y luego rinde mal en datos nuevos. Suele indicar falta de generalización.

### • Anomalía
Dato o comportamiento que se desvía significativamente del resto. En ciberseguridad puede señalar actividades maliciosas o no autorizadas.

---
