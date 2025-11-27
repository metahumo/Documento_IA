
---

# Buenas prácticas para escribir herramientas seguras

Este documento complementa la documentación principal y describe principios fundamentales para implementar herramientas robustas y seguras en agentes de IA, evitando vulnerabilidades comunes y comportamientos peligrosos.

Cuando dotamos a un agente de capacidades para interactuar con el sistema de archivos o ejecutar acciones, es crucial establecer límites claros y validaciones apropiadas. Una herramienta mal diseñada puede comprometer la integridad de nuestro sistema o causar pérdida de datos.

---

## 1. Validación de rutas y directorios

### Principio
Nunca confíes ciegamente en las rutas que el modelo proporciona. Una validación rigurosa evita escrituras o lecturas en ubicaciones no autorizadas.

### Implementación básica

**Establece un directorio base permitido**
```python
class Agent:
    def __init__(self):
        self.allowed_directory = os.path.abspath("./workspace")
        os.makedirs(self.allowed_directory, exist_ok=True)
```

**Valida que la ruta esté dentro del directorio permitido**
```python
def validate_path(self, filepath):
    """Verifica que la ruta esté dentro del directorio autorizado"""
    absolute_path = os.path.abspath(filepath)
    
    if not absolute_path.startswith(self.allowed_directory):
        raise ValueError(f"Acceso denegado: {filepath} está fuera del directorio autorizado")
    
    return absolute_path
```

**Aplica la validación en todas las herramientas**
```python
def read_file_content(self, filepath):
    try:
        validated_path = self.validate_path(filepath)
        
        with open(validated_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "status": "success",
            "content": content
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Archivo no encontrado"
        }
```

### Por qué importa
Sin validación, el modelo podría intentar acceder a:
- Archivos del sistema: `/etc/passwd`, `C:\Windows\System32\`
- Archivos de configuración sensibles: `.env`, `config.json`
- Directorios de otros usuarios

---

## 2. Límites en tamaño de archivos

### Principio
Establece límites razonables para evitar consumo excesivo de memoria o almacenamiento.

### Implementación

**Define límites de tamaño**
```python
class Agent:
    def __init__(self):
        self.max_file_size = 5 * 1024 * 1024  # 5 MB
        self.max_content_length = 100000  # 100k caracteres
```

**Valida antes de leer**
```python
def read_file_content(self, filepath):
    try:
        validated_path = self.validate_path(filepath)
        
        # Verifica tamaño antes de leer
        file_size = os.path.getsize(validated_path)
        if file_size > self.max_file_size:
            return {
                "status": "error",
                "message": f"Archivo demasiado grande: {file_size} bytes (máximo: {self.max_file_size})"
            }
        
        with open(validated_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "status": "success",
            "content": content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

**Valida antes de escribir**
```python
def create_files(self, directory=".", filename=None, content=""):
    try:
        # Valida longitud del contenido
        if len(content) > self.max_content_length:
            return {
                "status": "error",
                "message": f"Contenido demasiado largo: {len(content)} caracteres (máximo: {self.max_content_length})"
            }
        
        # Resto de la implementación...
```

### Por qué importa
Sin límites, el modelo podría:
- Crear archivos enormes que llenen el disco
- Intentar leer archivos binarios gigantes en memoria
- Causar fallas por agotamiento de recursos

---

## 3. Validación de nombres de archivo

### Principio
Restringe caracteres peligrosos y patrones problemáticos en nombres de archivo.

### Implementación

**Lista de caracteres no permitidos**
```python
import re

def validate_filename(self, filename):
    """Valida que el nombre de archivo sea seguro"""
    
    # Caracteres prohibidos en nombres de archivo
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1f]'
    
    if re.search(forbidden_chars, filename):
        raise ValueError(f"Nombre de archivo contiene caracteres no permitidos: {filename}")
    
    # Evita nombres reservados en Windows
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        raise ValueError(f"Nombre de archivo reservado por el sistema: {filename}")
    
    # Evita nombres que empiecen con punto (archivos ocultos sensibles)
    if filename.startswith('.'):
        raise ValueError(f"No se permiten archivos que empiecen con punto: {filename}")
    
    return filename
```

**Aplicación en herramienta**
```python
def create_files(self, directory=".", filename=None, content=""):
    try:
        if isinstance(filename, str):
            filename = [filename]
        
        # Valida cada nombre de archivo
        for name in filename:
            self.validate_filename(name)
        
        # Resto de la implementación...
```

### Por qué importa
Nombres maliciosos pueden:
- Sobrescribir archivos del sistema
- Crear archivos ocultos con configuración sensible
- Causar errores en diferentes sistemas operativos

---

## 4. Manejo seguro de excepciones

### Principio
Nunca expongas información sensible del sistema en mensajes de error. Proporciona mensajes útiles pero seguros.

### Implementación

**❌ Expone demasiada información**
```python
def read_file_content(self, filepath):
    with open(filepath, "r") as f:
        return f.read()
```

Si falla, el traceback completo muestra:
- Rutas absolutas del sistema
- Estructura de directorios
- Información de entorno

**✅ Manejo controlado**
```python
def read_file_content(self, filepath):
    try:
        validated_path = self.validate_path(filepath)
        
        with open(validated_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        print(f"\n[+] Archivo leído correctamente: {os.path.basename(filepath)}\n")
        
        return {
            "status": "success",
            "filepath": os.path.basename(filepath),  # Solo nombre, no ruta completa
            "content": content
        }
    
    except ValueError as e:
        # Error de validación (ruta no autorizada)
        print(f"\n[!] Error de validación: {e}\n")
        return {
            "status": "error",
            "message": "Acceso no autorizado"
        }
    
    except FileNotFoundError:
        # Archivo no existe
        print(f"\n[!] Archivo no encontrado: {os.path.basename(filepath)}\n")
        return {
            "status": "error",
            "message": "Archivo no encontrado"
        }
    
    except PermissionError:
        # Sin permisos de lectura
        print(f"\n[!] Permiso denegado: {os.path.basename(filepath)}\n")
        return {
            "status": "error",
            "message": "Permiso denegado"
        }
    
    except UnicodeDecodeError:
        # Archivo binario o codificación incorrecta
        print(f"\n[!] Error de codificación: {os.path.basename(filepath)}\n")
        return {
            "status": "error",
            "message": "No se pudo leer el archivo (posiblemente es binario)"
        }
    
    except Exception as e:
        # Cualquier otro error
        print(f"\n[!] Error inesperado al leer archivo\n")
        return {
            "status": "error",
            "message": "Error al leer el archivo"
        }
```

### Por qué importa
Mensajes de error detallados pueden:
- Revelar estructura de directorios
- Exponer nombres de usuarios del sistema
- Dar pistas sobre vulnerabilidades

---

## 5. Restricción de extensiones de archivo

### Principio
Limita las operaciones solo a tipos de archivo específicos según el propósito de la herramienta.

### Implementación

**Define extensiones permitidas**
```python
class Agent:
    def __init__(self):
        self.allowed_extensions = {'.md', '.txt', '.json', '.yaml', '.yml'}
```

**Valida extensión antes de operar**
```python
def validate_extension(self, filepath):
    """Verifica que la extensión esté permitida"""
    _, ext = os.path.splitext(filepath)
    
    if ext.lower() not in self.allowed_extensions:
        raise ValueError(f"Extensión no permitida: {ext}. Permitidas: {', '.join(self.allowed_extensions)}")
    
    return True
```

**Aplica en herramientas**
```python
def create_files(self, directory=".", filename=None, content=""):
    try:
        if isinstance(filename, str):
            filename = [filename]
        
        for name in filename:
            self.validate_filename(name)
            self.validate_extension(name)  # <- Validación adicional
        
        # Resto de la implementación...
```

### Por qué importa
Sin restricciones, el modelo podría:
- Crear scripts ejecutables (`.sh`, `.bat`, `.exe`)
- Modificar archivos de configuración críticos
- Sobrescribir archivos del sistema

---

## 6. Prevención de sobrescritura accidental

### Principio
Requiere confirmación explícita o verifica existencia antes de sobrescribir archivos.

### Implementación

**Opción 1: Verifica existencia y rechaza**
```python
def create_files(self, directory=".", filename=None, content=""):
    try:
        validated_dir = self.validate_path(directory)
        
        if isinstance(filename, str):
            filename = [filename]
        
        created_files = []
        
        for name in filename:
            self.validate_filename(name)
            self.validate_extension(name)
            
            file_path = os.path.join(validated_dir, name)
            
            # Rechaza si ya existe
            if os.path.exists(file_path):
                return {
                    "status": "error",
                    "message": f"El archivo ya existe: {name}"
                }
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            created_files.append(name)
        
        return {
            "status": "success",
            "files": created_files
        }
```

**Opción 2: Agrega parámetro overwrite explícito**
```python
def create_files(self, directory=".", filename=None, content="", overwrite=False):
    # En JSON Schema
    {
        "type": "function",
        "name": "create_files_in_dir",
        "parameters": {
            "type": "object",
            "properties": {
                # ...otros parámetros
                "overwrite": {
                    "type": "boolean",
                    "description": "Permitir sobrescribir archivos existentes",
                    "default": False
                }
            }
        }
    }
    
    # En la implementación
    if os.path.exists(file_path) and not overwrite:
        return {
            "status": "error",
            "message": f"El archivo ya existe: {name}. Usa overwrite=true para sobrescribir"
        }
```

### Por qué importa
Sin protección:
- Archivos importantes pueden perderse sin recuperación
- Datos críticos pueden ser sobrescritos accidentalmente

---

## 7. Logging y auditoría

### Principio
Registra todas las operaciones de herramientas para debugging y auditoría de seguridad.

### Implementación

**Sistema de logging básico**
```python
import logging
from datetime import datetime

class Agent:
    def __init__(self):
        # Configurar logging
        self.setup_logging()
        # Resto de inicialización...
    
    def setup_logging(self):
        """Configura sistema de logging"""
        log_dir = os.path.join(self.allowed_directory, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"agent_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # También imprime en consola
            ]
        )
        
        self.logger = logging.getLogger(__name__)
```

**Registra operaciones en herramientas**
```python
def create_files(self, directory=".", filename=None, content=""):
    self.logger.info(f"Iniciando create_files: dir={directory}, files={filename}")
    
    try:
        # Validaciones...
        # Operaciones...
        
        self.logger.info(f"Archivos creados exitosamente: {created_files}")
        
        return {
            "status": "success",
            "files": created_files
        }
    
    except Exception as e:
        self.logger.error(f"Error en create_files: {str(e)}")
        return {
            "status": "error",
            "message": "Error al crear archivos"
        }
```

### Por qué importa
Los logs permiten:
- Detectar intentos de acceso no autorizado
- Rastrear qué archivos fueron modificados y cuándo
- Depurar problemas después de que ocurren

---

## 8. Límite de operaciones por sesión

### Principio
Previene uso excesivo o abusivo estableciendo límites en el número de operaciones.

### Implementación

**Contador de operaciones**
```python
class Agent:
    def __init__(self):
        self.operation_counts = {
            "create": 0,
            "read": 0,
            "edit": 0
        }
        self.max_operations = {
            "create": 50,
            "read": 100,
            "edit": 50
        }
```

**Verifica antes de ejecutar**
```python
def create_files(self, directory=".", filename=None, content=""):
    # Verifica límite
    if self.operation_counts["create"] >= self.max_operations["create"]:
        return {
            "status": "error",
            "message": f"Límite de operaciones de creación alcanzado ({self.max_operations['create']})"
        }
    
    try:
        # Operaciones...
        
        # Incrementa contador
        self.operation_counts["create"] += len(created_files)
        
        return {
            "status": "success",
            "files": created_files
        }
```

### Por qué importa
Sin límites:
- El agente podría crear miles de archivos sin control
- Consumo excesivo de recursos
- Posibles ataques de denegación de servicio

---

## 9. Sanitización de contenido

### Principio
Valida y limpia el contenido antes de escribirlo, especialmente si proviene de fuentes externas.

### Implementación

**Validación básica de contenido**
```python
def sanitize_content(self, content):
    """Valida y limpia contenido antes de escribir"""
    
    # Verifica que no sea vacío
    if not content or not content.strip():
        raise ValueError("El contenido no puede estar vacío")
    
    # Límite de longitud
    if len(content) > self.max_content_length:
        raise ValueError(f"Contenido demasiado largo: {len(content)} caracteres")
    
    # Remueve caracteres de control peligrosos (excepto \n, \r, \t)
    sanitized = ''.join(char for char in content if char.isprintable() or char in '\n\r\t')
    
    return sanitized
```

**Aplica en herramientas**
```python
def create_files(self, directory=".", filename=None, content=""):
    try:
        # Sanitiza contenido
        clean_content = self.sanitize_content(content)
        
        # Resto de operaciones con clean_content...
```

### Por qué importa
Contenido no validado puede:
- Contener caracteres de control que corrompan archivos
- Incluir secuencias de escape que causen problemas
- Tener formato incorrecto que genere errores

---

## 10. Configuración por entorno

### Principio
Permite diferentes niveles de seguridad según el entorno (desarrollo, producción).

### Implementación

**Configuración flexible**
```python
import os

class Agent:
    def __init__(self, environment="development"):
        self.environment = environment
        
        if self.environment == "production":
            self.allowed_directory = os.path.abspath("./workspace")
            self.max_file_size = 1 * 1024 * 1024  # 1 MB
            self.max_operations = {"create": 10, "read": 50, "edit": 10}
            self.allowed_extensions = {'.md', '.txt'}
        
        elif self.environment == "development":
            self.allowed_directory = os.path.abspath("./dev_workspace")
            self.max_file_size = 10 * 1024 * 1024  # 10 MB
            self.max_operations = {"create": 100, "read": 200, "edit": 100}
            self.allowed_extensions = {'.md', '.txt', '.json', '.yaml', '.py'}
        
        os.makedirs(self.allowed_directory, exist_ok=True)
```

**Uso en main.py**
```python
# En desarrollo: más permisivo
agent = Agent(environment="development")

# En producción: más restrictivo
agent = Agent(environment="production")
```

### Por qué importa
Diferentes contextos requieren diferentes controles:
- Desarrollo: más flexible para pruebas
- Producción: máxima seguridad y restricciones

---

## Resumen de prácticas esenciales

| Práctica | Objetivo | Impacto si se omite |
|----------|----------|---------------------|
| Validación de rutas | Prevenir acceso no autorizado | Archivos del sistema expuestos |
| Límites de tamaño | Evitar consumo excesivo | Agotamiento de recursos |
| Validación de nombres | Prevenir nombres problemáticos | Errores multiplataforma |
| Manejo de excepciones | Ocultar detalles del sistema | Exposición de información |
| Restricción de extensiones | Limitar tipos de archivo | Ejecución de código malicioso |
| Prevención de sobrescritura | Proteger datos existentes | Pérdida de información |
| Logging | Auditoría de operaciones | Sin trazabilidad |
| Límite de operaciones | Prevenir abuso | Denegación de servicio |
| Sanitización de contenido | Validar datos de entrada | Corrupción de archivos |
| Configuración por entorno | Adaptar controles al contexto | Seguridad inadecuada |

---

## Ejemplo de herramienta completa con todas las prácticas

```python
def create_files(self, directory=".", filename=None, content=""):
    """Crea archivos con todas las validaciones de seguridad"""
    
    # Logging
    self.logger.info(f"Iniciando create_files: dir={directory}, files={filename}")
    
    try:
        # 1. Validar límite de operaciones
        if self.operation_counts["create"] >= self.max_operations["create"]:
            raise ValueError(f"Límite de operaciones alcanzado: {self.max_operations['create']}")
        
        # 2. Validar directorio
        validated_dir = self.validate_path(directory)
        
        # 3. Convertir a lista si es string
        if isinstance(filename, str):
            filename = [filename]
        
        # 4. Sanitizar contenido
        clean_content = self.sanitize_content(content)
        
        # 5. Validar cada archivo
        for name in filename:
            self.validate_filename(name)
            self.validate_extension(name)
        
        created_files = []
        
        # 6. Crear archivos
        for name in filename:
            file_path = os.path.join(validated_dir, name)
            
            # 7. Verificar existencia
            if os.path.exists(file_path):
                raise ValueError(f"El archivo ya existe: {name}")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(clean_content)
            
            created_files.append(name)
        
        # 8. Incrementar contador
        self.operation_counts["create"] += len(created_files)
        
        # 9. Logging exitoso
        self.logger.info(f"Archivos creados: {created_files}")
        
        return {
            "status": "success",
            "files": created_files
        }
    
    except ValueError as e:
        self.logger.warning(f"Validación fallida: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    
    except Exception as e:
        self.logger.error(f"Error inesperado: {e}")
        return {
            "status": "error",
            "message": "Error al crear archivos"
        }
```

---

Con estas prácticas implementadas, nuestras herramientas serán más robustas, seguras y predecibles, minimizando riesgos y mejorando la confiabilidad del agente en cualquier entorno.

---
