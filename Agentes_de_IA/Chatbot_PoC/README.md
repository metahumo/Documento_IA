[![Estado](https://img.shields.io/badge/estado-PoC-blue.svg)](#) 

# Chatbot_PoC · Agente de IA con Herramientas (Function Calling)

Este proyecto es una prueba de concepto (PoC) de un agente / chatbot en Python que interactúa con la API Responses de OpenAI, manteniendo memoria conversacional y ejecutando herramientas (funciones) para operar sobre el sistema de archivos (crear, leer y editar archivos Markdown u otros textos) de forma controlada. Toda la documentación complementaria está en la carpeta `docs/` y el código fuente en `src/`.

## Objetivos

- Mostrar los fundamentos para construir un agente con: contexto, memoria, razonamiento básico y ejecución de herramientas.
- Ilustrar el uso de la OpenAI Responses API con soporte para function calling.
- Servir como base modular para futuras extensiones (más herramientas, validaciones, logging, seguridad).

## Características Clave

- Memoria de conversación persistente en `agent.messages` (roles: system, user, assistant, function_call procesado como mensaje assistant).
- Herramientas disponibles:
	- `create_files_in_dir`: creación de uno o varios archivos `.md` con contenido dado.
	- `read_file`: lectura segura de archivos de texto.
	- `edit_file`: sustitución completa del contenido de un archivo.
- Prevención de llamadas duplicadas consecutivas (firma de llamada: nombre + argumentos ordenados).
- Re-consulta automática tras una llamada a herramienta para permitir al modelo reaccionar al resultado.
- Código simple y fácilmente extensible (clase `Agent`).
- Buenas prácticas documentadas para seguridad, debugging y manejo de errores (ver `docs/`).

## Estructura del Proyecto

```
Chatbot_PoC/
├── README.md              # Este documento
├── docs/                  # Documentación conceptual y guías
│   ├── Documentación.md
│   ├── Buenas prácticas para escribir herramientas seguras.md
│   ├── Cómo debuggear llamadas a herramientas del modelo.md
│   ├── Cómo detectar errores típicos en agentes con herramientas.md
│   ├── Estructura mínima recomendada para un agente modular.md
│   └── Tipos de parámetros en herramientas.md
└── src/
		├── main.py            # Punto de entrada, loop interactivo
		└── agent.py           # Clase Agent: herramientas + procesamiento
```

## Arquitectura Resumida

La clase `Agent`:
- Inicializa el historial con un mensaje `system` (estilo / reglas).
- Declara los esquemas JSON (JSON Schema) de cada herramienta en `setup_tools()`.
- Implementa cada herramienta como método Python (`create_files`, `read_file_content`, `edit_file_content`).
- Procesa la respuesta del modelo en `process_response(response)` diferenciando:
	- `function_call`: ejecuta herramienta, añade resultado como mensaje `assistant`.
	- `message`: extrae texto y lo almacena.
- Evita la repetición accidental comparando la firma de la última llamada.

Flujo de `main.py` (ciclo básico):
1. Leer input del usuario.
2. Validar comandos de salida (`exit`, `bye`, `fin`).
3. Añadir mensaje del usuario al historial.
4. Llamar al modelo con `input=agent.messages` y `tools=agent.tools`.
5. Procesar la respuesta. Si hubo tool call, hacer una segunda (única) llamada para la “respuesta final”.

## Definición de Herramientas (Schemas)

Ejemplo (fragmentos reales de `agent.py`):
```jsonc
{
	"type": "function",
	"name": "create_files_in_dir",
	"description": "Crear archivos en formato Markdown (.md) en el directorio actual o uno dado",
	"parameters": {
		"type": "object",
		"properties": {
			"directory": {"type": "string", "description": "Directorio en el que se crearán los archivos"},
			"filename": {"type": "array", "items": {"type": "string"}, "description": "Lista de nombres de archivos .md a crear"},
			"content": {"type": "string", "description": "Contenido en formato Markdown que tendrán los archivos"}
		},
		"required": ["directory", "filename"]
	}
}
```
Otros schemas: `read_file` (parámetro `filepath`), `edit_file` (`filepath`, `content`). Ver detalles en `agent.py` y ampliaciones conceptuales en `docs/Tipos de parámetros en herramientas.md`.

## Memoria Conversacional

- El historial `messages` incluye los mensajes del usuario y del asistente, más los resultados serializados de herramientas (como contenido `assistant`).
- Esto permite que el modelo razone con el contexto previo y el resultado de acciones ya ejecutadas.

## Instalación y Puesta en Marcha

Requisitos: Python 3.10+ (recomendado) y una API Key de OpenAI.

```powershell
# 1. Crear entorno virtual
python -m venv env
./env/Scripts/Activate.ps1

# 2. Instalar dependencias mínimas
pip install openai python-dotenv

# 3. Crear archivo .env (no incluido en el repo por seguridad)
echo OPENAI_API_KEY=tu_clave_aqui > .env

# 4. Ejecutar
python src/main.py
```

Salida esperada inicial:
```
Mi primer agente de IA
Tú: 
```

Comandos de salida: `exit`, `bye`, `fin`.

## Ejemplos de Uso

1. Conversación simple:

```
Tú: Hola, ¿qué puedes hacer?
Asistente: (respuesta según prompt system)
```

2. Crear un archivo:

```
Tú: Crea un archivo README_TEST.md en el directorio actual con un título y una lista de tres puntos.
```

El modelo debería invocar `create_files_in_dir` y luego mostrar el resultado.
3. Leer un archivo:

```
Tú: Lee el contenido del archivo README_TEST.md
```

4. Editar un archivo:

```
Tú: Actualiza el archivo README_TEST.md para que solo contenga un encabezado nuevo que diga "Archivo actualizado".
```

## Buenas Prácticas (Resumen)

Basado en `docs/Buenas prácticas para escribir herramientas seguras.md`:

- Validar rutas (restringir a un directorio permitido) y nombres de archivo (evitar caracteres peligrosos, reservados y archivos ocultos).
- Limitar tamaño de archivos leídos y longitud de contenido a escribir.
- Manejar excepciones de forma controlada (sin exponer rutas internas completas al usuario final si se evoluciona a modo producción).
- Sanitizar contenido antes de escribir (caracteres de control, longitud, formato).
- Registrar operaciones (logging) y limitar número de acciones por sesión para evitar abusos.
- Definir extensiones permitidas según el caso de uso (`.md`, `.txt`, etc.).

## Debugging (Resumen)

Ver: `docs/Cómo debuggear llamadas a herramientas del modelo.md`.

- Añadir impresiones estructuradas en: entrada usuario, antes/después de llamada al modelo, detección de `function_call`.
- Inspeccionar `response.output` (iterar y mostrar tipos, argumentos raw / parseados).
- Implementar modo debug opcional (flag o variable de entorno) para activar trazas.
- Exportar sesión (historial + llamadas a herramientas) para análisis offline.


## Errores Típicos (Resumen)
Ver: `docs/Cómo detectar errores típicos en agentes con herramientas.md`.

- Herramienta no se invoca: falta `tools` en la llamada o descripción ambigua.
- Argumentos incorrectos: nombres distintos entre schema y firma Python.
- Resultado ignorado: no se agrega al historial y el modelo “olvida” la acción.
- Llamadas repetidas: ausencia de verificación de firma (`last_tool_call`).
- Excepciones sin control: falta de bloques `try/except` en herramientas.
- Historial desbordado: agregar contenido excesivo (no truncar resultados grandes).

## Extender con Nuevas Herramientas

Pasos sugeridos (ver doc: `Estructura mínima recomendada para un agente modular.md`):

1. Definir el schema JSON (nombre único, descripción clara, parámetros con tipos correctos y `required`).
2. Implementar método en `Agent` (o mover a módulo futuro `tools/` cuando se module). 
3. Añadir schema a la lista `self.tools` en `setup_tools()`.
4. Ampliar `process_response` con la rama correspondiente (`elif fn_name == "nombre"`).
5. Serializar resultado como mensaje `assistant`.
6. (Opcional) Implementar validaciones y logging.

## Roadmap Sugerido

- Modularizar herramientas (`tools/file_tools.py`, validadores y logger separados).
- Añadir validaciones avanzadas: límite de operaciones, extensiones permitidas, sanitización de contenido.
- Integrar logging estructurado (JSON) + exportación de sesiones.
- Implementar resumen automático para historial largo.
- Añadir nuevas herramientas (cálculo, búsqueda web, análisis de texto). 
- Tests unitarios de cada herramienta y del flujo `process_response`.

## Referencias

- `docs/Documentación.md` – Tutorial paso a paso de construcción del agente.
- `docs/Tipos de parámetros en herramientas.md` – Guía breve de JSON Schema para function calling.
- `docs/Buenas prácticas para escribir herramientas seguras.md` – Seguridad y robustez.
- `docs/Cómo debuggear llamadas a herramientas del modelo.md` – Técnicas de inspección y trazas.
- `docs/Cómo detectar errores típicos en agentes con herramientas.md` – Patrón de fallos habituales.
- `docs/Estructura mínima recomendada para un agente modular.md` – Escalabilidad y organización.

## FAQ Rápido

- ¿Dónde defino nuevas herramientas? → En `Agent.setup_tools()` (luego se modulariza).
- ¿Cómo evito repetir acciones? → Firma con `(fn_name, json.dumps(args, sort_keys=True))`.
- ¿Por qué el resultado de la herramienta se guarda como `assistant`? → La Responses API no admite rol `tool`; se integra como respuesta adicional para mantener contexto.
- ¿Cómo salgo del chat? → Escribe `exit`, `bye` o `fin`.

## Licencia

PoC educativa.

---

