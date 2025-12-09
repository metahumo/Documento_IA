[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/metahumo/Documento_IA) [![LinkedIn](https://img.shields.io/badge/LinkedIn-MiPerfil-blue?logo=linkedin)](https://www.linkedin.com/in/daniel-moises-castro-perez/)

# Documento IA — Índice maestro

Exploramos, organizamos y documentamos aprendizajes prácticos sobre agentes de IA, LLMs y desarrollo de PoCs con herramientas (function calling). El objetivo es construir una guía clara, reproducible y pedagógica para crear asistentes que razonan, recuerdan y ejecutan acciones seguras sobre el entorno.

## Cómo usar este README

- Usa este índice para navegar por las carpetas principales del repositorio.
- Cada carpeta incluye documentación (`docs/`), ejemplos y código (`src/`).
- Antes de ejecutar código, revisa "Buenas prácticas y seguridad" y prepara tu `.env` (claves/API Keys fuera del repositorio).

## Estructura principal (carpetas)

### Agente de IA / Chatbot_PoC
PoC de un chatbot/agente en Python usando OpenAI Responses API con herramientas: crear, leer y editar archivos, memoria conversacional, prevención de llamadas duplicadas y re-consulta tras tool calling. Incluye guías de seguridad, debugging y estructura modular mínima.
- Código y docs: `Agente de IA/Chatbot_PoC/`
- Guía completa: [Chatbot_PoC/README.md](Agente_de_IA/Chatbot_PoC/README.md)

### Machine Learning
Material introductorio y aplicado sobre fundamentos y preparación de datos para modelos de ML, con énfasis en casos y paralelos en ciberseguridad.

#### Introducción al ML
- Carpeta: `Machine Learning/Introducción al ML/`
- Documentos incluidos:
    - `Los Datos en ML.md`: importancia de la calidad, fuentes (internas, públicas, tiempo real, usuario), limpieza, features y división entrenamiento/prueba.
    - `Tipos de ML.md`: aprendizaje supervisado, no supervisado y por refuerzo; ejemplos generales y de ciberseguridad; glosario (regresión, clasificación, clustering, agente, recompensa, política, features, overfitting, anomalía).
    - `Técnicas Avanzadas de Preprocesamiento en ML.md`: feature engineering, reducción de dimensionalidad (PCA, t-SNE, autoencoders), normalización, manejo de desbalance (SMOTE, oversampling, pesos), codificación categórica y aplicaciones (tráfico, malware, anomalías, correlación multi‑fuente).

#### Mini Proyectos de ML (Ejercicios)
- Carpeta: `Ejercicios/`
- Proyectos incluidos:
    - **Regresión Lineal Simple (Celsius → Fahrenheit)**: `Ejercicios/Regresion_lineal/`
        - `Primer_modelo.py`: primer modelo de ML end-to-end con visualización, carga de datos (`celsius.csv`), features/etiquetas, entrenamiento y predicción.
        - Conceptos: scatter plots, reshape, `.fit()` y `.predict()`, score R².
    - **Regresión Lineal Avanzada (Housing Dataset)**: `Ejercicios/Regresion_lineal_housing/`
        - `regresion_lineal_housing.py`: flujo completo: exploración (`.info()`, `.describe()`, histogramas), limpieza (dropna), one-hot encoding, feature engineering (`bedroom_ratio`), correlaciones, train/test split, estandarización (StandardScaler), evaluación (R², MSE, RMSE).
        - `regresion_lineal_housing.ipynb`: versión interactiva del análisis con visualizaciones geográficas y gráficas de correlación.
        - `housing.csv`: dataset con características de viviendas (ubicación, población, habitaciones, etc.) y precios (`median_house_value`).

### Automatización_Microsoft
Documentación y guías prácticas sobre automatización de procesos en Microsoft 365 usando Power Platform, enfocado en optimizar tareas repetitivas y aumentar productividad en entornos corporativos.

#### Introducción a Power Platform
- Carpeta: `Automatización_Microsoft/`
- Documentos incluidos:
    - `Introducción a Power Platform.md`: conceptos fundamentales, herramientas disponibles (Power Automate, Power Apps, Power BI) y buenas prácticas.

#### Power Automate
- Carpeta: `Automatización_Microsoft/Power_Automate/`
- Documentos incluidos:
    - `01. Introducción a Power Automate.md`: guía introductoria sobre automatización de flujos de trabajo, triggers, acciones y conectores.
    - `02. Caso práctico - Obtener archivo adjunto de mail en OneDrive.md`: ejemplo paso a paso para automatizar descarga de adjuntos desde Outlook a OneDrive.

## Índice rápido
- Agente de IA → [Chatbot_PoC](Agente_de_IA/Chatbot_PoC/)
- Machine Learning → [Introducción al ML](Machine%20Learning/Introducción%20al%20ML/)
- Automatización Microsoft → [Power_Automate](Automatización_Microsoft/Power_Automate/)

## Buenas prácticas y seguridad

- No subas claves ni tokens: usa `.env` y variables de entorno.
- Lee y entiende las herramientas antes de ejecutarlas (operan sobre el sistema de archivos).
- Limita el alcance del agente (directorios permitidos, tamaños máximos, extensiones seguras).
- Maneja excepciones y logs; evita exponer rutas o datos sensibles en errores.

## Cómo contribuir

1. Fork del repo.
2. Crea rama `feature/…` o `fix/…` con cambios acotados.
3. Pull Request con descripción breve, archivos modificados y, si aplica, capturas o pasos de prueba.
4. Etiquetas y revisión colaborativa.

## Créditos

Este repositorio se apoya en materiales públicos y de la comunidad de IA/AGI. Gran parte de la PoC de `Chatbot_PoC` se inspira en recursos educativos como la documentación de OpenAI y tutoriales introductorios (ver referencias en su README interno). Todo el mérito corresponde a sus autores originales.

## Advertencias legales y éticas

El contenido tiene fines educativos. Úsalo de forma responsable y conforme a las leyes aplicables. No automatices acciones que vulneren términos de servicio, privacidad o propiedad intelectual. Si dudas, solicita asesoría o evita su ejecución.
## Licencia
Material en su mayoría de carácter educativo y de referencia (revisar cada carpeta para detalles sobre licencias o notas adicionales).

---
