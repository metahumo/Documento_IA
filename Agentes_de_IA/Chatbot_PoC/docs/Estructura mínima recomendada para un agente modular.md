
---

# Estructura mínima recomendada para un agente modular

Este documento complementa la documentación principal y proporciona una arquitectura base para organizar agentes de IA de forma escalable, mantenible y modular.

A medida que un agente crece en funcionalidad, mantener todo el código en uno o dos archivos se vuelve inmanejable. Una estructura modular permite agregar herramientas, configuraciones y capacidades sin comprometer la claridad del código ni la facilidad de mantenimiento.

---

## 1. Estructura de archivos básica

### Organización recomendada

```
proyecto_agente/
│
├── main.py                    # Punto de entrada, loop principal
├── agent.py                   # Clase Agent con lógica core
├── .env                       # Variables de entorno (API keys)
├── requirements.txt           # Dependencias del proyecto
│
├── tools/                     # Módulo de herramientas
│   ├── __init__.py
│   ├── file_tools.py         # Herramientas de archivos
│   ├── web_tools.py          # Herramientas web (opcional)
│   └── data_tools.py         # Herramientas de datos (opcional)
│
├── config/                    # Configuración
│   ├── __init__.py
│   └── settings.py           # Configuración centralizada
│
├── utils/                     # Utilidades
│   ├── __init__.py
│   ├── validators.py         # Funciones de validación
│   └── logger.py             # Sistema de logging
│
└── workspace/                 # Directorio de trabajo del agente
    └── logs/                  # Logs de operaciones
```

### Ventajas de esta estructura

- **Separación de responsabilidades**: cada módulo tiene un propósito claro
- **Escalabilidad**: agregar herramientas no requiere modificar código existente
- **Mantenibilidad**: cambios en una herramienta no afectan a otras
- **Testabilidad**: módulos independientes son más fáciles de probar

---

## 2. Archivo principal: `main.py`

### Responsabilidad
Punto de entrada de la aplicación. Maneja el loop de interacción con el usuario y coordina las llamadas al modelo.

### Implementación mínima

```python
"""
Punto de entrada principal del agente de IA
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

from agent import Agent
from config.settings import Settings

def main():
    """Función principal que ejecuta el agente"""
    
    # Cargar configuración
    load_dotenv()
    settings = Settings()
    
    # Inicializar cliente y agente
    client = OpenAI()
    agent = Agent(settings=settings)
    
    print(f"\n{settings.WELCOME_MESSAGE}\n")
    
    # Loop principal
    while True:
        try:
            user_input = input("Tú: ").strip()
            
            # Validaciones básicas
            if not user_input:
                continue
            
            if user_input.lower() in settings.EXIT_COMMANDS:
                print(f"\n{settings.GOODBYE_MESSAGE}\n")
                break
            
            # Agregar mensaje del usuario
            agent.add_user_message(user_input)
            
            # Llamada inicial al modelo
            response = client.responses.create(
                model=settings.MODEL_NAME,
                input=agent.messages,
                tools=agent.tools
            )
            
            # Procesar respuesta
            called_tool = agent.process_response(response)
            
            # Re-consulta si se usó una herramienta
            if called_tool:
                response = client.responses.create(
                    model=settings.MODEL_NAME,
                    input=agent.messages,
                    tools=agent.tools
                )
                agent.process_response(response)
        
        except KeyboardInterrupt:
            print(f"\n\n{settings.GOODBYE_MESSAGE}\n")
            break
        
        except Exception as e:
            print(f"\n[ERROR] {e}\n")
            if settings.DEBUG_MODE:
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    main()
```

### Características clave
- Manejo de excepciones robusto
- Configuración centralizada
- Separación clara entre UI y lógica
- Fácil de extender (agregar comandos especiales, etc.)

---

## 3. Clase principal: `agent.py`

### Responsabilidad
Encapsula la lógica del agente: gestión de mensajes, procesamiento de respuestas y coordinación de herramientas.

### Implementación modular

```python
"""
Clase Agent: núcleo del agente de IA
"""
import json
from datetime import datetime

from tools.file_tools import FileTools
from utils.validators import PathValidator
from utils.logger import AgentLogger

class Agent:
    """Agente de IA con soporte para herramientas"""
    
    def __init__(self, settings=None):
        """
        Inicializa el agente con configuración
        
        Args:
            settings: Objeto Settings con configuración
        """
        self.settings = settings
        
        # Sistema de logging
        self.logger = AgentLogger(settings)
        
        # Validadores
        self.path_validator = PathValidator(settings.ALLOWED_DIRECTORY)
        
        # Herramientas
        self.file_tools = FileTools(
            validator=self.path_validator,
            logger=self.logger,
            settings=settings
        )
        
        # Estado del agente
        self.messages = [
            {"role": "system", "content": settings.SYSTEM_PROMPT}
        ]
        self.last_tool_call = None
        self.operation_counts = {"create": 0, "read": 0, "edit": 0}
        
        # Configurar herramientas disponibles
        self.tools = self._setup_tools()
        
        self.logger.info("Agente inicializado correctamente")
    
    def _setup_tools(self):
        """Configura las herramientas disponibles para el modelo"""
        return [
            self.file_tools.get_create_schema(),
            self.file_tools.get_read_schema(),
            self.file_tools.get_edit_schema()
        ]
    
    def add_user_message(self, content):
        """Agrega un mensaje del usuario al historial"""
        self.messages.append({"role": "user", "content": content})
        self.logger.debug(f"Mensaje de usuario agregado: {content[:50]}...")
    
    def process_response(self, response):
        """
        Procesa la respuesta del modelo
        
        Returns:
            bool: True si se ejecutó una herramienta, False si no
        """
        for output in response.output:
            if output.type == "function_call":
                return self._handle_function_call(output)
            
            elif output.type == "message":
                self._handle_message(output)
        
        return False
    
    def _handle_function_call(self, output):
        """Maneja una llamada a función del modelo"""
        fn_name = output.name
        args = json.loads(output.arguments)
        
        self.logger.info(f"Llamada a herramienta: {fn_name}")
        self.logger.debug(f"Argumentos: {args}")
        
        # Verificar duplicados
        call_signature = (fn_name, json.dumps(args, sort_keys=True))
        if self.last_tool_call == call_signature:
            self.logger.warning("Llamada duplicada detectada, omitiendo")
            return False
        
        # Ejecutar herramienta correspondiente
        result = self._execute_tool(fn_name, args)
        
        # Actualizar estado
        self.last_tool_call = call_signature
        
        # Agregar resultado al historial
        self.messages.append({
            "role": "assistant",
            "content": f"[Resultado de {fn_name}]: {json.dumps(result)}"
        })
        
        return True
    
    def _execute_tool(self, fn_name, args):
        """Ejecuta la herramienta correspondiente"""
        
        # Incrementar contador
        operation_type = fn_name.split("_")[0]  # "create", "read", "edit"
        if operation_type in self.operation_counts:
            self.operation_counts[operation_type] += 1
        
        # Ejecutar según el nombre
        if fn_name == "create_files_in_dir":
            return self.file_tools.create_files(**args)
        elif fn_name == "read_file":
            return self.file_tools.read_file(**args)
        elif fn_name == "edit_file":
            return self.file_tools.edit_file(**args)
        else:
            self.logger.error(f"Herramienta desconocida: {fn_name}")
            return {
                "status": "error",
                "message": f"Herramienta desconocida: {fn_name}"
            }
    
    def _handle_message(self, output):
        """Maneja un mensaje de texto del modelo"""
        reply = "\n".join(part.text for part in output.content)
        print(f"Asistente: {reply}")
        
        self.messages.append({"role": "assistant", "content": reply})
        self.logger.debug(f"Respuesta del asistente: {reply[:50]}...")
```

### Características clave
- Inyección de dependencias (settings, logger, validator)
- Separación de herramientas en módulos externos
- Gestión centralizada del estado
- Logging integrado
- Fácil de extender con nuevas herramientas

---

## 4. Módulo de herramientas: `tools/file_tools.py`

### Responsabilidad
Implementa todas las herramientas relacionadas con archivos. Cada módulo de herramientas debe ser independiente.

### Implementación

```python
"""
Herramientas para operaciones con archivos
"""
import os
import json

class FileTools:
    """Agrupa todas las herramientas de manipulación de archivos"""
    
    def __init__(self, validator, logger, settings):
        """
        Inicializa las herramientas de archivos
        
        Args:
            validator: PathValidator para validación de rutas
            logger: AgentLogger para logging
            settings: Configuración del agente
        """
        self.validator = validator
        self.logger = logger
        self.settings = settings
    
    # ==================== SCHEMAS ====================
    
    def get_create_schema(self):
        """Retorna el schema JSON para crear archivos"""
        return {
            "type": "function",
            "name": "create_files_in_dir",
            "description": "Crear archivos en formato Markdown (.md) en el directorio actual o uno dado",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directorio en el que se crearán los archivos"
                    },
                    "filename": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de nombres de archivos .md a crear"
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenido en formato Markdown que tendrán los archivos"
                    }
                },
                "required": ["directory", "filename"]
            }
        }
    
    def get_read_schema(self):
        """Retorna el schema JSON para leer archivos"""
        return {
            "type": "function",
            "name": "read_file",
            "description": "Leer el contenido de un archivo",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Ruta completa del archivo a leer"
                    }
                },
                "required": ["filepath"]
            }
        }
    
    def get_edit_schema(self):
        """Retorna el schema JSON para editar archivos"""
        return {
            "type": "function",
            "name": "edit_file",
            "description": "Editar el contenido de un archivo existente",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Ruta completa del archivo a editar"
                    },
                    "content": {
                        "type": "string",
                        "description": "Nuevo contenido del archivo"
                    }
                },
                "required": ["filepath", "content"]
            }
        }
    
    # ==================== IMPLEMENTACIONES ====================
    
    def create_files(self, directory=".", filename=None, content=""):
        """
        Crea archivos en el directorio especificado
        
        Args:
            directory: Directorio donde crear los archivos
            filename: Nombre o lista de nombres de archivos
            content: Contenido a escribir en los archivos
        
        Returns:
            dict: Resultado de la operación con status y datos
        """
        self.logger.info(f"Iniciando create_files en {directory}")
        
        try:
            # Validar directorio
            validated_dir = self.validator.validate_path(directory)
            
            # Convertir a lista si es necesario
            if isinstance(filename, str):
                filename = [filename]
            
            # Validar contenido
            if len(content) > self.settings.MAX_CONTENT_LENGTH:
                raise ValueError(f"Contenido demasiado largo: {len(content)} caracteres")
            
            # Crear directorio si no existe
            os.makedirs(validated_dir, exist_ok=True)
            
            created_files = []
            
            # Crear cada archivo
            for name in filename:
                file_path = os.path.join(validated_dir, name)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                created_files.append(name)
                self.logger.info(f"Archivo creado: {name}")
            
            return {
                "status": "success",
                "files": created_files
            }
        
        except Exception as e:
            self.logger.error(f"Error en create_files: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def read_file(self, filepath):
        """
        Lee el contenido de un archivo
        
        Args:
            filepath: Ruta del archivo a leer
        
        Returns:
            dict: Resultado con status y contenido
        """
        self.logger.info(f"Leyendo archivo: {filepath}")
        
        try:
            validated_path = self.validator.validate_path(filepath)
            
            # Verificar tamaño
            file_size = os.path.getsize(validated_path)
            if file_size > self.settings.MAX_FILE_SIZE:
                raise ValueError(f"Archivo demasiado grande: {file_size} bytes")
            
            with open(validated_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.logger.info(f"Archivo leído exitosamente: {filepath}")
            
            return {
                "status": "success",
                "filepath": os.path.basename(filepath),
                "content": content
            }
        
        except FileNotFoundError:
            self.logger.warning(f"Archivo no encontrado: {filepath}")
            return {
                "status": "error",
                "message": "Archivo no encontrado"
            }
        
        except Exception as e:
            self.logger.error(f"Error en read_file: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def edit_file(self, filepath, content):
        """
        Edita el contenido de un archivo existente
        
        Args:
            filepath: Ruta del archivo a editar
            content: Nuevo contenido del archivo
        
        Returns:
            dict: Resultado de la operación
        """
        self.logger.info(f"Editando archivo: {filepath}")
        
        try:
            validated_path = self.validator.validate_path(filepath)
            
            # Validar contenido
            if len(content) > self.settings.MAX_CONTENT_LENGTH:
                raise ValueError(f"Contenido demasiado largo: {len(content)} caracteres")
            
            with open(validated_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.logger.info(f"Archivo editado exitosamente: {filepath}")
            
            return {
                "status": "success",
                "filepath": os.path.basename(filepath),
                "message": "Archivo actualizado"
            }
        
        except FileNotFoundError:
            self.logger.warning(f"Archivo no encontrado: {filepath}")
            return {
                "status": "error",
                "message": "Archivo no encontrado"
            }
        
        except Exception as e:
            self.logger.error(f"Error en edit_file: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
```

### Características clave
- Schemas y funciones en el mismo módulo
- Validación consistente en todas las operaciones
- Logging integrado
- Manejo de errores robusto
- Fácil de probar de forma aislada

---

## 5. Configuración centralizada: `config/settings.py`

### Responsabilidad
Centraliza toda la configuración del agente en un solo lugar, facilitando ajustes y diferentes entornos.

### Implementación

```python
"""
Configuración centralizada del agente
"""
import os

class Settings:
    """Configuración del agente de IA"""
    
    def __init__(self):
        """Carga configuración desde variables de entorno y valores por defecto"""
        
        # ==================== API ====================
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5-nano")
        
        # ==================== PATHS ====================
        self.WORKSPACE_DIR = os.path.abspath(
            os.getenv("WORKSPACE_DIR", "./workspace")
        )
        self.ALLOWED_DIRECTORY = self.WORKSPACE_DIR
        self.LOGS_DIR = os.path.join(self.WORKSPACE_DIR, "logs")
        
        # Crear directorios si no existen
        os.makedirs(self.WORKSPACE_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        
        # ==================== LÍMITES ====================
        self.MAX_FILE_SIZE = int(
            os.getenv("MAX_FILE_SIZE", 5 * 1024 * 1024)  # 5 MB
        )
        self.MAX_CONTENT_LENGTH = int(
            os.getenv("MAX_CONTENT_LENGTH", 100000)  # 100k caracteres
        )
        self.MAX_OPERATIONS = {
            "create": int(os.getenv("MAX_CREATE_OPS", 50)),
            "read": int(os.getenv("MAX_READ_OPS", 100)),
            "edit": int(os.getenv("MAX_EDIT_OPS", 50))
        }
        
        # ==================== EXTENSIONES ====================
        self.ALLOWED_EXTENSIONS = {'.md', '.txt', '.json', '.yaml', '.yml'}
        
        # ==================== MENSAJES ====================
        self.SYSTEM_PROMPT = os.getenv(
            "SYSTEM_PROMPT",
            "Eres un asistente útil, preciso, que habla español y eres muy conciso con tus respuestas"
        )
        self.WELCOME_MESSAGE = "Mi primer agente de IA"
        self.GOODBYE_MESSAGE = "¡Hasta luego!"
        self.EXIT_COMMANDS = {"exit", "bye", "fin", "salir"}
        
        # ==================== DEBUG ====================
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    def __repr__(self):
        """Representación de la configuración"""
        return f"Settings(model={self.MODEL_NAME}, workspace={self.WORKSPACE_DIR})"
```

### Características clave
- Variables de entorno para configuración flexible
- Valores por defecto sensatos
- Centralización de todos los parámetros
- Fácil de modificar para diferentes entornos

---

## 6. Validadores: `utils/validators.py`

### Responsabilidad
Agrupa todas las funciones de validación reutilizables.

### Implementación

```python
"""
Validadores reutilizables para el agente
"""
import os
import re

class PathValidator:
    """Valida rutas y nombres de archivo"""
    
    def __init__(self, allowed_directory):
        """
        Inicializa el validador con un directorio permitido
        
        Args:
            allowed_directory: Directorio base autorizado
        """
        self.allowed_directory = os.path.abspath(allowed_directory)
    
    def validate_path(self, filepath):
        """
        Valida que una ruta esté dentro del directorio permitido
        
        Args:
            filepath: Ruta a validar
        
        Returns:
            str: Ruta absoluta validada
        
        Raises:
            ValueError: Si la ruta está fuera del directorio permitido
        """
        absolute_path = os.path.abspath(filepath)
        
        if not absolute_path.startswith(self.allowed_directory):
            raise ValueError(
                f"Acceso denegado: {filepath} está fuera del directorio autorizado"
            )
        
        return absolute_path
    
    def validate_filename(self, filename):
        """
        Valida que un nombre de archivo sea seguro
        
        Args:
            filename: Nombre del archivo
        
        Returns:
            str: Nombre validado
        
        Raises:
            ValueError: Si el nombre no es válido
        """
        # Caracteres prohibidos
        forbidden_chars = r'[<>:"/\\|?*\x00-\x1f]'
        if re.search(forbidden_chars, filename):
            raise ValueError(
                f"Nombre de archivo contiene caracteres no permitidos: {filename}"
            )
        
        # Nombres reservados en Windows
        reserved_names = {
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        }
        
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in reserved_names:
            raise ValueError(
                f"Nombre de archivo reservado por el sistema: {filename}"
            )
        
        # Archivos ocultos
        if filename.startswith('.'):
            raise ValueError(
                f"No se permiten archivos que empiecen con punto: {filename}"
            )
        
        return filename
    
    def validate_extension(self, filepath, allowed_extensions):
        """
        Valida que la extensión del archivo esté permitida
        
        Args:
            filepath: Ruta del archivo
            allowed_extensions: Set de extensiones permitidas
        
        Returns:
            bool: True si es válida
        
        Raises:
            ValueError: Si la extensión no está permitida
        """
        _, ext = os.path.splitext(filepath)
        
        if ext.lower() not in allowed_extensions:
            raise ValueError(
                f"Extensión no permitida: {ext}. "
                f"Permitidas: {', '.join(allowed_extensions)}"
            )
        
        return True
```

### Características clave
- Reutilizable en múltiples herramientas
- Validaciones robustas y seguras
- Mensajes de error claros
- Fácil de probar unitariamente

---

## 7. Sistema de logging: `utils/logger.py`

### Responsabilidad
Proporciona logging consistente en todo el agente.

### Implementación

```python
"""
Sistema de logging para el agente
"""
import logging
import os
from datetime import datetime

class AgentLogger:
    """Wrapper de logging con configuración específica del agente"""
    
    def __init__(self, settings):
        """
        Inicializa el sistema de logging
        
        Args:
            settings: Objeto Settings con configuración
        """
        self.settings = settings
        
        # Configurar logger
        self.logger = logging.getLogger("AgentAI")
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Evitar duplicación de handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura los handlers de logging"""
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler de archivo
        log_file = os.path.join(
            self.settings.LOGS_DIR,
            f"agent_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler de consola (solo si debug)
        if self.settings.DEBUG_MODE:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """Log nivel DEBUG"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log nivel INFO"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log nivel WARNING"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log nivel ERROR"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log nivel CRITICAL"""
        self.logger.critical(message)
```

### Características clave
- Logging a archivo automático
- Rotación por día
- Niveles configurables
- Consola solo en modo debug

---

## 8. Archivo de dependencias: `requirements.txt`

### Contenido mínimo

```
openai>=2.0.0
python-dotenv>=1.0.0
```

### Instalación

```bash
pip install -r requirements.txt
```

---

## 9. Variables de entorno: `.env`

### Estructura recomendada

```env
# API Configuration
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
MODEL_NAME=gpt-5-nano

# Paths
WORKSPACE_DIR=./workspace

# Limits
MAX_FILE_SIZE=5242880
MAX_CONTENT_LENGTH=100000
MAX_CREATE_OPS=50
MAX_READ_OPS=100
MAX_EDIT_OPS=50

# Prompts
SYSTEM_PROMPT=Eres un asistente útil, preciso, que habla español y eres muy conciso con tus respuestas

# Debug
DEBUG_MODE=false
LOG_LEVEL=INFO
```

---

## 10. Cómo agregar una nueva herramienta

### Pasos para extender el agente

**1. Crear el módulo de herramienta**
```python
# tools/calculation_tools.py

class CalculationTools:
    """Herramientas de cálculo matemático"""
    
    def __init__(self, logger, settings):
        self.logger = logger
        self.settings = settings
    
    def get_calculate_schema(self):
        """Schema para operación de cálculo"""
        return {
            "type": "function",
            "name": "calculate",
            "description": "Realiza operaciones matemáticas básicas",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "Operación a realizar"
                    },
                    "a": {
                        "type": "number",
                        "description": "Primer número"
                    },
                    "b": {
                        "type": "number",
                        "description": "Segundo número"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }
    
    def calculate(self, operation, a, b):
        """Implementación del cálculo"""
        self.logger.info(f"Calculando: {a} {operation} {b}")
        
        try:
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    raise ValueError("División por cero")
                result = a / b
            else:
                raise ValueError(f"Operación desconocida: {operation}")
            
            return {
                "status": "success",
                "result": result
            }
        
        except Exception as e:
            self.logger.error(f"Error en calculate: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
```

**2. Integrar en agent.py**
```python
# Importar
from tools.calculation_tools import CalculationTools

# En __init__
self.calc_tools = CalculationTools(
    logger=self.logger,
    settings=settings
)

# En _setup_tools
def _setup_tools(self):
    return [
        self.file_tools.get_create_schema(),
        self.file_tools.get_read_schema(),
        self.file_tools.get_edit_schema(),
        self.calc_tools.get_calculate_schema()  # <- Nueva herramienta
    ]

# En _execute_tool
elif fn_name == "calculate":
    return self.calc_tools.calculate(**args)
```

**3. Listo**
El agente ahora puede usar la nueva herramienta sin modificar `main.py` ni otras partes del código.

---

## Beneficios de esta arquitectura

| Aspecto | Beneficio |
|---------|-----------|
| **Escalabilidad** | Agregar herramientas no requiere cambios en código existente |
| **Mantenibilidad** | Cada módulo tiene responsabilidad única y clara |
| **Testabilidad** | Módulos independientes son fáciles de probar |
| **Reutilización** | Validadores y utilidades compartidas en todo el proyecto |
| **Configurabilidad** | Settings centralizadas permiten diferentes entornos |
| **Debugging** | Logging consistente facilita identificar problemas |
| **Colaboración** | Estructura clara facilita trabajo en equipo |

---

## Ejemplo de uso completo

```bash
# 1. Clonar/crear proyecto
mkdir mi_agente && cd mi_agente

# 2. Crear estructura
mkdir -p tools config utils workspace/logs

# 3. Crear archivos principales (copiar código de arriba)

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar .env
echo "OPENAI_API_KEY=tu-clave-aqui" > .env

# 6. Ejecutar
python main.py
```

---

Con esta estructura modular, nuestro agente estará preparado para crecer de forma ordenada, manteniendo la claridad del código y facilitando el mantenimiento a largo plazo. Cada nuevo desarrollador podrá entender rápidamente la arquitectura y contribuir sin romper funcionalidad existente.

---

