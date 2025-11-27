
---

# Cómo debuggear llamadas a herramientas del modelo

Este documento complementa la documentación principal y proporciona técnicas prácticas para rastrear, analizar y resolver problemas en las llamadas a herramientas que realiza el modelo de IA.

Cuando un agente usa herramientas, el flujo de ejecución se vuelve más complejo. Los mensajes no solo viajan del usuario al modelo y viceversa, sino que también invocan funciones y procesan sus resultados. Debuggear este flujo requiere visibilidad en cada etapa del proceso.

---

## 1. Impresiones estratégicas en puntos clave

### Principio
Coloca mensajes informativos en los puntos críticos del flujo para seguir la ejecución paso a paso.

### Implementación básica

**En la entrada del usuario**
```python
# main.py
user_input = input("Tú: ").strip()

if user_input:
    print(f"\n[DEBUG] Input del usuario: '{user_input}'")
    print(f"[DEBUG] Longitud: {len(user_input)} caracteres\n")
```

**Antes de llamar al modelo**
```python
response = client.responses.create(
    model="gpt-5-nano",
    input=agent.messages,
    tools=agent.tools
)

print(f"\n[DEBUG] Llamada al modelo completada")
print(f"[DEBUG] Número de mensajes en historial: {len(agent.messages)}")
print(f"[DEBUG] Herramientas disponibles: {len(agent.tools)}\n")
```

**Al detectar llamada a herramienta**
```python
# agent.py - en process_response
if output.type == "function_call":
    fn_name = output.name
    args = json.loads(output.arguments)
    
    print(f"\n{'='*60}")
    print(f"[DEBUG] LLAMADA A HERRAMIENTA DETECTADA")
    print(f"{'='*60}")
    print(f"Función: {fn_name}")
    print(f"Argumentos recibidos:")
    print(json.dumps(args, indent=2, ensure_ascii=False))
    print(f"{'='*60}\n")
```

**Resultado de la herramienta**
```python
result = self.create_files(**args)

print(f"\n[DEBUG] Resultado de la herramienta:")
print(json.dumps(result, indent=2, ensure_ascii=False))
print()
```

### Ventaja
Estas impresiones nos permiten ver exactamente qué está pasando en cada momento sin necesidad de un debugger complejo.

---

## 2. Inspección del historial de mensajes

### Principio
El historial (`messages`) es el estado completo de la conversación. Inspeccionarlo revela qué información tiene el modelo en cada momento.

### Técnicas de inspección

**Función helper para mostrar historial**
```python
# agent.py
def debug_print_history(self):
    """Imprime el historial completo de mensajes de forma legible"""
    print(f"\n{'='*60}")
    print(f"HISTORIAL DE MENSAJES ({len(self.messages)} mensajes)")
    print(f"{'='*60}\n")
    
    for i, msg in enumerate(self.messages, 1):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        # Trunca contenido muy largo
        display_content = content if len(content) < 200 else content[:200] + "..."
        
        print(f"{i}. [{role.upper()}]")
        print(f"   {display_content}")
        print()
    
    print(f"{'='*60}\n")
```

**Uso en puntos estratégicos**
```python
# main.py - después de agregar mensaje del usuario
agent.messages.append({"role": "user", "content": user_input})
agent.debug_print_history()  # Ver estado antes de llamar al modelo

# Después de procesar respuesta
agent.process_response(response)
agent.debug_print_history()  # Ver cómo cambió el historial
```

**Inspección selectiva por rol**
```python
def count_messages_by_role(self):
    """Cuenta mensajes por tipo de rol"""
    counts = {}
    for msg in self.messages:
        role = msg.get("role", "unknown")
        counts[role] = counts.get(role, 0) + 1
    
    print(f"\n[DEBUG] Distribución de mensajes:")
    for role, count in counts.items():
        print(f"  - {role}: {count}")
    print()
```

### Ventaja
Ver el historial completo ayuda a detectar:
- Mensajes duplicados
- Resultados de herramientas que no se agregaron
- Contexto que el modelo está recibiendo

---

## 3. Tracking de llamadas a herramientas

### Principio
Mantén un registro detallado de cada invocación de herramienta para análisis posterior.

### Implementación

**Sistema de tracking básico**
```python
# agent.py
class Agent:
    def __init__(self):
        self.tool_call_log = []  # Registro de llamadas
        # Resto de inicialización...
```

**Registrar cada llamada**
```python
def process_response(self, response):
    for output in response.output:
        if output.type == "function_call":
            fn_name = output.name
            args = json.loads(output.arguments)
            
            # Crear registro de llamada
            call_record = {
                "timestamp": datetime.now().isoformat(),
                "function": fn_name,
                "arguments": args,
                "result": None,
                "success": False
            }
            
            # Ejecutar herramienta
            try:
                if fn_name == "create_files_in_dir":
                    result = self.create_files(**args)
                elif fn_name == "read_file":
                    result = self.read_file_content(**args)
                elif fn_name == "edit_file":
                    result = self.edit_file_content(**args)
                else:
                    result = {"status": "error", "message": f"Herramienta desconocida: {fn_name}"}
                
                # Actualizar registro
                call_record["result"] = result
                call_record["success"] = result.get("status") == "success"
                
            except Exception as e:
                call_record["result"] = {"status": "error", "message": str(e)}
                call_record["success"] = False
            
            # Guardar registro
            self.tool_call_log.append(call_record)
```

**Función para revisar log**
```python
def debug_print_tool_log(self):
    """Muestra el historial completo de llamadas a herramientas"""
    print(f"\n{'='*60}")
    print(f"LOG DE HERRAMIENTAS ({len(self.tool_call_log)} llamadas)")
    print(f"{'='*60}\n")
    
    for i, call in enumerate(self.tool_call_log, 1):
        status = "✓" if call["success"] else "✗"
        print(f"{i}. [{status}] {call['function']} - {call['timestamp']}")
        print(f"   Argumentos: {call['arguments']}")
        print(f"   Resultado: {call['result']}")
        print()
    
    print(f"{'='*60}\n")
```

**Exportar log a archivo**
```python
def export_tool_log(self, filename="tool_calls.json"):
    """Exporta el log de herramientas a un archivo JSON"""
    import json
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(self.tool_call_log, f, indent=2, ensure_ascii=False)
    print(f"\n[DEBUG] Log exportado a {filename}\n")
```

### Ventaja
Un log persistente permite:
- Analizar patrones de uso de herramientas
- Identificar llamadas fallidas recurrentes
- Revisar qué pasó después de una sesión

---

## 4. Validación de argumentos antes de ejecutar

### Principio
Verifica que los argumentos recibidos cumplan con lo esperado antes de pasarlos a la función.

### Implementación

**Función de validación**
```python
def validate_tool_arguments(self, fn_name, args):
    """Valida que los argumentos sean correctos para la herramienta"""
    
    errors = []
    
    if fn_name == "create_files_in_dir":
        if "directory" not in args:
            errors.append("Falta parámetro requerido: directory")
        if "filename" not in args:
            errors.append("Falta parámetro requerido: filename")
        
        if "filename" in args:
            if not isinstance(args["filename"], (str, list)):
                errors.append("filename debe ser string o lista")
    
    elif fn_name == "read_file":
        if "filepath" not in args:
            errors.append("Falta parámetro requerido: filepath")
        
        if "filepath" in args and not isinstance(args["filepath"], str):
            errors.append("filepath debe ser string")
    
    elif fn_name == "edit_file":
        if "filepath" not in args:
            errors.append("Falta parámetro requerido: filepath")
        if "content" not in args:
            errors.append("Falta parámetro requerido: content")
        
        if "content" in args and not isinstance(args["content"], str):
            errors.append("content debe ser string")
    
    if errors:
        print(f"\n[DEBUG] ❌ ERRORES DE VALIDACIÓN:")
        for error in errors:
            print(f"  - {error}")
        print()
        return False
    
    print(f"\n[DEBUG] ✓ Validación de argumentos exitosa\n")
    return True
```

**Uso antes de ejecutar**
```python
if output.type == "function_call":
    fn_name = output.name
    args = json.loads(output.arguments)
    
    # Validar antes de ejecutar
    if not self.validate_tool_arguments(fn_name, args):
        result = {
            "status": "error",
            "message": "Argumentos inválidos"
        }
    else:
        # Ejecutar herramienta
        if fn_name == "create_files_in_dir":
            result = self.create_files(**args)
        # ...resto de herramientas
```

### Ventaja
Detecta problemas de tipo y estructura antes de que causen excepciones en las funciones.

---

## 5. Comparación de firma de llamada

### Principio
Compara las llamadas actuales con las anteriores para detectar repeticiones o patrones anómalos.

### Implementación

**Función de comparación**
```python
def debug_compare_call_signature(self, fn_name, args):
    """Compara la llamada actual con la anterior"""
    
    current_signature = (fn_name, json.dumps(args, sort_keys=True))
    
    print(f"\n[DEBUG] Comparación de firmas:")
    print(f"  Llamada actual: {fn_name}")
    print(f"  Argumentos actuales: {json.dumps(args, sort_keys=True)}")
    
    if self.last_tool_call:
        print(f"  Última función: {self.last_tool_call[0]}")
        print(f"  Últimos argumentos: {self.last_tool_call[1]}")
        
        if current_signature == self.last_tool_call:
            print(f"  ⚠️  DUPLICADO DETECTADO")
        else:
            print(f"  ✓ Llamada diferente")
    else:
        print(f"  ℹ️  Primera llamada de la sesión")
    
    print()
```

**Uso en process_response**
```python
if output.type == "function_call":
    fn_name = output.name
    args = json.loads(output.arguments)
    
    # Comparar con llamada anterior
    self.debug_compare_call_signature(fn_name, args)
    
    # Verificar duplicado
    call_signature = (fn_name, json.dumps(args, sort_keys=True))
    if self.last_tool_call == call_signature:
        print("[DEBUG] ⚠️  Llamada duplicada omitida")
        return False
```

### Ventaja
Identifica inmediatamente cuándo el modelo está intentando repetir acciones.

---

## 6. Inspección de la respuesta del modelo

### Principio
Analiza la estructura completa de `response.output` para entender qué está devolviendo el modelo.

### Implementación

**Función de inspección detallada**
```python
def debug_inspect_response(self, response):
    """Analiza en detalle la respuesta del modelo"""
    
    print(f"\n{'='*60}")
    print(f"INSPECCIÓN DE RESPUESTA DEL MODELO")
    print(f"{'='*60}\n")
    
    print(f"Número de elementos en output: {len(response.output)}")
    print()
    
    for i, output in enumerate(response.output, 1):
        print(f"Elemento {i}:")
        print(f"  Tipo: {output.type}")
        
        if output.type == "function_call":
            print(f"  Función: {output.name}")
            print(f"  Argumentos (raw): {output.arguments}")
            
            try:
                args = json.loads(output.arguments)
                print(f"  Argumentos (parsed):")
                print(f"    {json.dumps(args, indent=4, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Error al parsear argumentos: {e}")
        
        elif output.type == "message":
            print(f"  Contenido:")
            for part in output.content:
                text = part.text if hasattr(part, 'text') else str(part)
                display_text = text if len(text) < 150 else text[:150] + "..."
                print(f"    {display_text}")
        
        print()
    
    print(f"{'='*60}\n")
```

**Uso después de llamar al modelo**
```python
response = client.responses.create(
    model="gpt-5-nano",
    input=agent.messages,
    tools=agent.tools
)

# Inspeccionar respuesta completa
agent.debug_inspect_response(response)

# Procesar
agent.process_response(response)
```

### Ventaja
Ver la estructura raw de la respuesta ayuda a entender:
- Qué elementos está devolviendo el modelo
- Si hay múltiples llamadas a herramientas
- Problemas de formato en los argumentos

---

## 7. Modo debug configurable

### Principio
Permite activar/desactivar el debug sin modificar código, usando una variable de configuración.

### Implementación

**Variable de control**
```python
# agent.py
class Agent:
    def __init__(self, debug=False):
        self.debug_mode = debug
        # Resto de inicialización...
```

**Función helper para prints condicionales**
```python
def debug_print(self, message, force=False):
    """Imprime solo si debug_mode está activado"""
    if self.debug_mode or force:
        print(message)
```

**Uso en todas las funciones**
```python
def create_files(self, directory=".", filename=None, content=""):
    self.debug_print(f"\n[+] Herramienta iniciada: create_files")
    self.debug_print(f"    directory={directory}")
    self.debug_print(f"    filename={filename}")
    self.debug_print(f"    content_length={len(content)}\n")
    
    try:
        # Operaciones...
        
        self.debug_print(f"\n[+] Archivos creados: {created_files}\n")
        
        return {
            "status": "success",
            "files": created_files
        }
```

**Activación desde main.py**
```python
# Modo normal
agent = Agent(debug=False)

# Modo debug
agent = Agent(debug=True)

# Desde variable de entorno
import os
debug_enabled = os.getenv("AGENT_DEBUG", "false").lower() == "true"
agent = Agent(debug=debug_enabled)
```

### Ventaja
Control granular del nivel de información sin tocar el código de las herramientas.

---

## 8. Breakpoints manuales

### Principio
Pausa la ejecución en puntos críticos para inspeccionar el estado manualmente.

### Implementación

**Función de breakpoint**
```python
def debug_breakpoint(self, message="Breakpoint alcanzado"):
    """Pausa la ejecución y permite inspección manual"""
    
    if not self.debug_mode:
        return
    
    print(f"\n{'='*60}")
    print(f"🛑 {message}")
    print(f"{'='*60}\n")
    
    print("Comandos disponibles:")
    print("  h - Ver historial de mensajes")
    print("  t - Ver log de herramientas")
    print("  c - Continuar ejecución")
    print("  i - Inspeccionar variable (ej: 'i self.messages')")
    print()
    
    while True:
        cmd = input("debug> ").strip().lower()
        
        if cmd == "c":
            break
        elif cmd == "h":
            self.debug_print_history()
        elif cmd == "t":
            self.debug_print_tool_log()
        elif cmd.startswith("i "):
            var_name = cmd[2:].strip()
            try:
                print(eval(var_name))
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Comando no reconocido")
```

**Uso en puntos estratégicos**
```python
def process_response(self, response):
    for output in response.output:
        if output.type == "function_call":
            fn_name = output.name
            args = json.loads(output.arguments)
            
            # Breakpoint antes de ejecutar herramienta
            self.debug_breakpoint(f"Antes de ejecutar {fn_name}")
            
            # Ejecutar herramienta...
```

### Ventaja
Control total sobre la ejecución sin necesidad de un debugger externo.

---

## 9. Exportación de sesión completa

### Principio
Guarda toda la información de la sesión para análisis posterior offline.

### Implementación

**Función de exportación**
```python
def export_debug_session(self, filename="debug_session.json"):
    """Exporta toda la información de debug a un archivo"""
    
    session_data = {
        "timestamp": datetime.now().isoformat(),
        "message_history": self.messages,
        "tool_calls": self.tool_call_log,
        "tools_available": self.tools,
        "operation_counts": getattr(self, "operation_counts", {}),
        "last_tool_call": self.last_tool_call
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[DEBUG] Sesión exportada a {filename}\n")
```

**Uso al finalizar o en error**
```python
# main.py
try:
    while True:
        user_input = input("Tú: ").strip()
        
        if user_input.lower() in ("exit", "bye", "fin"):
            agent.export_debug_session()  # Exportar antes de salir
            print("\n¡Hasta luego!\n")
            break
        
        # Resto del código...

except Exception as e:
    print(f"\n[ERROR] Excepción no manejada: {e}\n")
    agent.export_debug_session("error_session.json")  # Exportar en error
    raise
```

### Ventaja
Permite analizar sesiones completas sin depender de logs en consola que pueden perderse.

---

## 10. Visualización de flujo de llamadas

### Principio
Genera una representación visual del flujo de ejecución para entender el orden de operaciones.

### Implementación

**Función de trazado**
```python
def debug_trace_flow(self, event, details=""):
    """Registra eventos de flujo con timestamp"""
    
    if not hasattr(self, "flow_trace"):
        self.flow_trace = []
    
    self.flow_trace.append({
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "details": details
    })
```

**Uso en puntos clave**
```python
# main.py
agent.debug_trace_flow("USER_INPUT", user_input)

response = client.responses.create(...)
agent.debug_trace_flow("MODEL_CALLED", f"{len(agent.messages)} mensajes enviados")

agent.process_response(response)
agent.debug_trace_flow("RESPONSE_PROCESSED")

# agent.py - en herramientas
def create_files(self, directory=".", filename=None, content=""):
    self.debug_trace_flow("TOOL_STARTED", f"create_files: {filename}")
    
    # Operaciones...
    
    self.debug_trace_flow("TOOL_FINISHED", f"create_files: {result['status']}")
```

**Visualización del flujo**
```python
def debug_print_flow(self):
    """Muestra el flujo completo de ejecución"""
    
    print(f"\n{'='*60}")
    print(f"FLUJO DE EJECUCIÓN")
    print(f"{'='*60}\n")
    
    for i, event in enumerate(self.flow_trace, 1):
        time = event["timestamp"].split("T")[1][:12]  # Solo hora
        print(f"{i}. [{time}] {event['event']}")
        if event["details"]:
            print(f"   └─ {event['details']}")
    
    print(f"\n{'='*60}\n")
```

### Ventaja
Ver el flujo completo ayuda a entender:
- Cuántas veces se llama al modelo
- Orden de ejecución de herramientas
- Tiempo entre operaciones

---

## Checklist de debugging

Cuando una herramienta no funciona como esperas, sigue esta secuencia:

1. ☐ **Verifica que `tools` esté en la llamada al modelo**
   ```python
   print(f"[DEBUG] tools={agent.tools}")
   ```

2. ☐ **Confirma que el modelo invoca la herramienta**
   ```python
   print(f"[DEBUG] output.type={output.type}")
   ```

3. ☐ **Revisa los argumentos recibidos**
   ```python
   print(f"[DEBUG] args={json.dumps(args, indent=2)}")
   ```

4. ☐ **Valida tipos y nombres de parámetros**
   ```python
   self.validate_tool_arguments(fn_name, args)
   ```

5. ☐ **Inspecciona el resultado de la herramienta**
   ```python
   print(f"[DEBUG] result={json.dumps(result, indent=2)}")
   ```

6. ☐ **Confirma que se agrega al historial**
   ```python
   print(f"[DEBUG] Historial después: {len(self.messages)} mensajes")
   ```

7. ☐ **Verifica que hay re-consulta si es necesaria**
   ```python
   print(f"[DEBUG] called_tool={called_tool}")
   ```

8. ☐ **Revisa el historial completo**
   ```python
   agent.debug_print_history()
   ```

9. ☐ **Exporta la sesión para análisis offline**
   ```python
   agent.export_debug_session()
   ```

---

## Ejemplo de sesión de debugging completa

```python
# main.py con debugging habilitado
from openai import OpenAI
from dotenv import load_dotenv
from agent import Agent

load_dotenv()
client = OpenAI()

# Activar modo debug
agent = Agent(debug=True)

print("\n[DEBUG] Agente inicializado con debug=True")
print(f"[DEBUG] Herramientas disponibles: {[t['name'] for t in agent.tools]}\n")

while True:
    user_input = input("Tú: ").strip()
    
    if not user_input:
        continue
    
    if user_input.lower() in ("exit", "bye", "fin"):
        print("\n[DEBUG] Finalizando sesión...")
        agent.debug_print_tool_log()
        agent.export_debug_session()
        print("\n¡Hasta luego!\n")
        break
    
    # Trazar evento
    agent.debug_trace_flow("USER_INPUT", user_input)
    
    # Agregar al historial
    agent.messages.append({"role": "user", "content": user_input})
    print(f"\n[DEBUG] Mensaje agregado. Total: {len(agent.messages)}")
    
    # Llamar al modelo
    print(f"[DEBUG] Llamando al modelo con {len(agent.tools)} herramientas...")
    response = client.responses.create(
        model="gpt-5-nano",
        input=agent.messages,
        tools=agent.tools
    )
    
    # Inspeccionar respuesta
    agent.debug_inspect_response(response)
    
    # Procesar
    called_tool = agent.process_response(response)
    
    # Re-consulta si necesario
    if called_tool:
        print(f"\n[DEBUG] Herramienta ejecutada. Haciendo re-consulta...")
        response = client.responses.create(
            model="gpt-5-nano",
            input=agent.messages,
            tools=agent.tools
        )
        agent.process_response(response)
    
    # Mostrar flujo
    agent.debug_print_flow()
```

---

Con estas técnicas de debugging, podremos identificar rápidamente dónde está el problema en el flujo de llamadas a herramientas y resolverlo de forma eficiente, manteniendo visibilidad completa sobre lo que el agente está haciendo en cada momento.

---

