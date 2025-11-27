
---

# Cómo detectar errores típicos en agentes con herramientas

Este documento complementa la documentación principal y describe los errores más comunes que surgen al implementar herramientas en agentes de IA, junto con estrategias para identificarlos y resolverlos de forma efectiva.

Cuando trabajamos con agentes que usan herramientas (function calling), es normal encontrarse con comportamientos inesperados. Reconocer estos patrones ayuda a depurar más rápido y evitar frustraciones innecesarias durante el desarrollo.

---

## 1. La herramienta nunca se invoca

### Síntomas
- El modelo responde con texto explicando lo que haría, pero nunca ejecuta la función
- El agente dice "no puedo hacer eso" cuando debería usar una herramienta

### Causas comunes

**Descripción poco clara o genérica**
```python
# ❌ Mal
"description": "Maneja archivos"

# ✅ Bien
"description": "Crear archivos en formato Markdown (.md) en el directorio actual o uno dado"
```

La descripción debe ser específica y orientada a la acción. El modelo necesita entender **cuándo** usar la herramienta.

**Parámetros mal documentados**
```python
# ❌ Mal
"filepath": {
    "type": "string",
    "description": "ruta"
}

# ✅ Bien
"filepath": {
    "type": "string",
    "description": "Ruta completa del archivo a leer"
}
```

Cada parámetro necesita una descripción que elimine ambigüedad sobre qué valor se espera.

**Herramientas no pasadas al modelo**
```python
# ❌ Falta el parámetro tools
response = client.responses.create(
    model="gpt-5-nano",
    input=agent.messages
)

# ✅ Correcto
response = client.responses.create(
    model="gpt-5-nano",
    input=agent.messages,
    tools=agent.tools  # <- Esencial
)
```

### Cómo verificar
- Revisa que el parámetro `tools` esté presente en la llamada al modelo
- Imprime `agent.tools` antes de la llamada para confirmar que contiene las definiciones
- Usa prompts muy directos: "crea un archivo llamado prueba.md" en lugar de peticiones ambiguas

---

## 2. El modelo invoca la herramienta con argumentos incorrectos

### Síntomas
- Se genera una excepción tipo `KeyError`, `TypeError` o `AttributeError`
- Los valores recibidos no coinciden con lo esperado (número en lugar de string, etc.)

### Causas comunes

**Nombres de parámetros inconsistentes**
```python
# En la definición JSON Schema
"parameters": {
    "properties": {
        "file_path": { "type": "string" }  # <- Usa guión bajo
    }
}

# En la función Python
def read_file(self, filepath):  # <- No coincide
    ...
```

Los nombres deben ser **idénticos** entre la definición de herramienta y la firma de la función Python.

**Tipo declarado no coincide con el uso**
```python
# Declaras como string
"content": { "type": "string" }

# Pero intentas usar como lista
for line in content:  # <- Falla si content es string
    ...
```

Si necesitas una lista, decláralo como `array`. Si necesitas texto, usa `string`.

**Parámetros marcados como required pero con valor por defecto**
```python
# En JSON Schema
"required": ["directory"]

# En Python
def create_files(self, directory="."):  # <- No es realmente requerido
    ...
```

Si tiene valor por defecto, no debe estar en `required`. Si está en `required`, la función debe esperarlo siempre.

### Cómo verificar
- Imprime `args` inmediatamente después de `json.loads(output.arguments)`:
  ```python
  args = json.loads(output.arguments)
  print(f"   - Argumentos recibidos: {args}")
  ```
- Compara los nombres de las claves en `args` con los parámetros de tu función
- Usa `try-except` específicos para capturar errores de tipo:
  ```python
  try:
      result = self.create_files(**args)
  except TypeError as e:
      print(f"Error de tipo en argumentos: {e}")
  ```

---

## 3. La herramienta se ejecuta pero no devuelve el resultado esperado

### Síntomas
- La herramienta termina sin errores pero el modelo no reacciona al resultado
- El agente repite la misma acción o dice "no pude hacerlo" después de ejecutar correctamente

### Causas comunes

**Resultado no agregado al historial**
```python
# ❌ Ejecutas pero no guardas el resultado
if fn_name == "read_file":
    result = self.read_file_content(**args)
    # Falta agregarlo a self.messages

# ✅ Correcto
if fn_name == "read_file":
    result = self.read_file_content(**args)
    self.messages.append({
        "role": "assistant",
        "content": f"[Resultado de {fn_name}]: {json.dumps(result)}"
    })
```

El modelo necesita ver el resultado en el historial para procesarlo y dar una respuesta coherente.

**No se hace re-consulta tras usar la herramienta**
```python
# ❌ Ejecutas herramienta pero no vuelves a llamar al modelo
called_tool = agent.process_response(response)
# Termina aquí, el modelo nunca procesa el resultado

# ✅ Correcto
called_tool = agent.process_response(response)
if called_tool:
    response = client.responses.create(
        model="gpt-5-nano",
        input=agent.messages,
        tools=agent.tools
    )
    agent.process_response(response)
```

**Resultado con formato incorrecto**
```python
# ❌ Devuelves string simple
return "Archivo leído"

# ✅ Devuelves objeto estructurado
return {
    "status": "success",
    "content": "contenido del archivo..."
}
```

Los resultados estructurados permiten al modelo entender mejor qué ocurrió y responder apropiadamente.

### Cómo verificar
- Imprime el historial completo después de ejecutar una herramienta:
  ```python
  print(f"\n[DEBUG] Historial actual: {json.dumps(self.messages, indent=2)}\n")
  ```
- Confirma que el último mensaje contiene el resultado de la herramienta
- Verifica que `called_tool` devuelve `True` cuando se ejecuta una función

---

## 4. El agente ejecuta la misma herramienta repetidamente

### Síntomas
- Se crea el mismo archivo múltiples veces
- La herramienta se invoca en bucle sin parar

### Causas comunes

**Sin prevención de duplicados**
```python
# ❌ No hay verificación
if fn_name == "create_files_in_dir":
    result = self.create_files(**args)
    # Se ejecuta siempre, incluso si es idéntica a la anterior

# ✅ Con verificación de firma
call_signature = (fn_name, json.dumps(args, sort_keys=True))
if self.last_tool_call == call_signature:
    print("\n[!] Llamada idéntica detectada. Se omite.\n")
    return False

self.last_tool_call = call_signature
result = self.create_files(**args)
```

**Bucle infinito de re-consultas**
```python
# ❌ while True sin condición de salida
while True:
    response = client.responses.create(...)
    agent.process_response(response)
    # Nunca sale del bucle

# ✅ Una sola re-consulta condicional
called_tool = agent.process_response(response)
if called_tool:
    response = client.responses.create(...)
    agent.process_response(response)
```

### Cómo verificar
- Añade un contador de iteraciones y límite máximo:
  ```python
  max_iterations = 5
  iteration = 0
  while iteration < max_iterations:
      iteration += 1
      print(f"[DEBUG] Iteración {iteration}")
      # ... resto del código
  ```
- Imprime la firma de cada llamada para ver si se repite:
  ```python
  print(f"[DEBUG] Firma de llamada: {call_signature}")
  ```

---

## 5. Excepciones no controladas en la herramienta

### Síntomas
- El script se detiene abruptamente con un traceback
- Mensajes de error de Python interrumpen la conversación

### Causas comunes

**Falta de bloques try-except**
```python
# ❌ Sin manejo de errores
def read_file_content(self, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# ✅ Con manejo de errores
def read_file_content(self, filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "status": "success",
            "content": content
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"Archivo no encontrado: {filepath}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

**Operaciones de archivo sin validación**
```python
# ❌ Asumes que el directorio existe
with open(filepath, "w") as f:
    f.write(content)

# ✅ Creas el directorio si no existe
os.makedirs(os.path.dirname(filepath), exist_ok=True)
with open(filepath, "w") as f:
    f.write(content)
```

### Cómo verificar
- Ejecuta casos extremos intencionalmente:
  - Rutas que no existen
  - Nombres de archivo con caracteres inválidos
  - Contenido vacío o muy largo
- Revisa que todas las herramientas devuelven objetos con `status` en lugar de lanzar excepciones

---

## 6. El historial crece demasiado y el modelo pierde contexto

### Síntomas
- Las respuestas se vuelven incoherentes después de varias interacciones
- El modelo parece "olvidar" información proporcionada anteriormente
- Errores relacionados con límite de tokens

### Causas comunes

**Agregado indiscriminado al historial**
```python
# ❌ Agregas todo sin filtrar
messages += response.output

# Mejor: Filtra solo lo necesario
for output in response.output:
    if output.type == "message":
        # Solo agrega mensajes relevantes
        messages.append({"role": "assistant", "content": ...})
```

**Resultados de herramientas muy largos**
```python
# ❌ Agregas contenido completo de archivos grandes
self.messages.append({
    "role": "assistant",
    "content": f"[Resultado]: {file_content}"  # Puede ser enorme
})

# ✅ Resumes o truncas contenido extenso
content_preview = file_content[:500] + "..." if len(file_content) > 500 else file_content
self.messages.append({
    "role": "assistant",
    "content": f"[Resultado]: {content_preview}"
})
```

### Cómo verificar
- Imprime la longitud del historial periódicamente:
  ```python
  print(f"[DEBUG] Mensajes en historial: {len(self.messages)}")
  ```
- Calcula tokens aproximados multiplicando caracteres por 0.25 (estimación básica)
- Implementa truncado automático si el historial supera cierto tamaño

---

## Resumen de verificaciones rápidas

| Problema | Verificación rápida |
|----------|---------------------|
| Herramienta no se invoca | ¿Está `tools` en la llamada al modelo? |
| Argumentos incorrectos | ¿Coinciden los nombres en JSON Schema y Python? |
| Resultado no se procesa | ¿Se agrega al historial y hay re-consulta? |
| Ejecuciones repetidas | ¿Hay verificación de firma de llamada? |
| Excepciones no controladas | ¿Todas las herramientas tienen try-except? |
| Historial muy largo | ¿Se filtra o trunca el contenido? |

---

## Estrategia general de depuración

1. **Añade prints informativos** en puntos clave:
   - Antes de invocar el modelo
   - Al detectar `function_call`
   - Tras ejecutar cada herramienta
   - Después de agregar al historial

2. **Usa mensajes de consola estructurados**:
   ```python
   print(f"\n[+] Herramienta iniciada: {fn_name}")
   print(f"   - Argumentos: {args}")
   print(f"   - Resultado: {result}")
   ```

3. **Valida tipos y estructuras**:
   ```python
   assert isinstance(args, dict), "args debe ser un diccionario"
   assert "filepath" in args, "falta parámetro filepath"
   ```

4. **Prueba casos extremos primero**:
   - Archivos inexistentes
   - Directorios sin permisos
   - Argumentos vacíos o nulos

5. **Revisa la documentación del modelo**:
   - No todos los modelos soportan herramientas igual
   - OpenAI Responses API tiene particularidades con roles
   - Confirma versiones compatibles

Con esta guía podrás identificar rápidamente dónde está el problema y aplicar la solución correcta, manteniendo nuestro agente robusto y predecible.

---

