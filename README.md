[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/metahumo/Documento_IA) [![LinkedIn](https://img.shields.io/badge/LinkedIn-MiPerfil-blue?logo=linkedin)](https://www.linkedin.com/in/daniel-moises-castro-perez/)

# Documento_IA

Inteligencia artificial en .md

Este repositorio contiene documentos, guías y pruebas de concepto (PoC) relacionados con agentes de IA, herramientas para interactuar con APIs de modelos y secciones prácticas sobre automatización en Microsoft 365.

---

## Contenido del repositorio

- Agentes_de_IA/ — Proyectos y PoC de agentes conversacionales y agentes con herramientas (function calling).
- Automatización_Microsoft/ — Guías y casos prácticos para automatizar procesos con Power Platform (Power Automate, Power Apps, Power BI).
- Notebooks y ejemplos en Python/Jupyter para experimentación y aprendizaje.

---

## Estructura (resumen)

```
Documento_IA/
├── Agentes_de_IA/
│   ├── Chatbot_PoC/
│   │   └── README.md
│   └── ... (otros agentes / demos)
├── Automatización_Microsoft/
│   ├── README.md
│   ├── Introducción a Power Platform.md
│   └── Power_Automate/
│       ├── README.md
│       ├── 01. Introducción a Power Automate.md
│       ├── 02. Caso práctico - Obtener archivo adjunto de mail en OneDrive.md
│       └── Images/
└── notebooks/ (Jupyter notebooks de ejemplo)
```

---

## Agentes de IA (ejemplo destacado)

En `Agentes_de_IA/Chatbot_PoC/` hay una prueba de concepto de un agente/chatbot en Python que usa la API Responses de OpenAI con soporte para function calling. Características destacadas:

- Memoria conversacional y serialización de resultados de herramientas.
- Herramientas (schemas + implementaciones) para crear, leer y editar archivos `.md`.
- Prevención de llamadas duplicadas y re-consulta automática tras ejecución de herramientas.
- Documentación adicional en `docs/` sobre buenas prácticas, debugging y diseño modular.

(Ver `Agentes_de_IA/Chatbot_PoC/README.md` para detalles e instrucciones de ejecución).

---

## Nuevo apartado: Automatización_Microsoft

He añadido aquí un apartado dedicado a la carpeta `Automatización_Microsoft/` para que quede reflejado en el README principal. A continuación se resume su contenido y propósito.

### Objetivo
Proveer documentación práctica y casos de uso para automatizar procesos en Microsoft 365 mediante Power Platform, con foco en:
- Eliminar tareas repetitivas.
- Reducir errores humanos.
- Aumentar la productividad mediante flujos automatizados e integraciones.

### Contenido principal
- Introducción a Power Platform: conceptos (Power Automate, Power Apps, Power BI) y buenas prácticas.
- Sección práctica sobre Power Automate con guías paso a paso y capturas para casos reales.
- Casos prácticos orientados a escenarios comunes en entornos corporativos.

### Power Automate — Guía y casos prácticos
Dentro de `Automatización_Microsoft/Power_Automate/` hay material orientado a aprender y aplicar Power Automate:

- 01. Introducción a Power Automate: conceptos clave (Triggers, Actions, Conectores, Flows) y tips.
- 02. Caso práctico — Obtener archivo adjunto de mail en OneDrive: guía con pasos claros, filtrado de correos, manejo de múltiples adjuntos y pruebas.
- Imágenes y capturas en `Power_Automate/Images/` que ayudan a seguir los pasos.

Resumen de ventajas de Power Automate:
- Automatiza el procesamiento de correos, organización de documentos, notificaciones (Teams), actualización de listas/databases y generación de informes.
- Integra aplicaciones del ecosistema Microsoft 365 mediante conectores.

### Buenas prácticas y seguridad
- Planificar el flujo antes de implementarlo.
- Revisar permisos y conectores usados.
- Testear con datos de prueba.
- Documentar la finalidad y auditoría de los flujos.
- Usar cuentas corporativas y revisar periódicamente flujos activos.

### Recursos y enlaces útiles
- Documentación oficial de Power Automate: https://learn.microsoft.com/power-automate/
- Microsoft Learn — cursos sobre Power Platform: https://learn.microsoft.com/training/power-automate/
- Power Automate Community: https://powerusers.microsoft.com/

(Ver `Automatización_Microsoft/README.md` y `Automatización_Microsoft/Power_Automate/README.md` para la documentación completa y los casos prácticos detallados).

---

## Cómo empezar (para las partes con código)

- Para los proyectos Python (p. ej. Chatbot_PoC):
  1. Crear entorno virtual (Python 3.10+ recomendado).
  2. Instalar dependencias: `pip install -r requirements.txt` o `pip install openai python-dotenv` según el PoC.
  3. Añadir variables de entorno (p. ej. OPENAI_API_KEY) en un `.env`.
  4. Ejecutar los scripts desde la carpeta del PoC (leer su README específico).

- Para Power Automate: necesitarás acceso a una cuenta de Microsoft 365 con permisos para crear flujos.

---

## Contribuciones
Mejoras y sugerencias son bienvenidas. Si quieres ampliar la sección de Automatización (más casos, scripts, plantillas de flujos o capturas), añade archivos en `Automatización_Microsoft/` y abre una propuesta de cambio en el repositorio.

---

## Licencia
Material en su mayoría de carácter educativo y de referencia (revisar cada carpeta para detalles sobre licencias o notas adicionales).

---
