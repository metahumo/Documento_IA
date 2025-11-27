
---

# Tipos de parámetros en herramientas (Function Calling)

Este documento complementa la explicación de herramientas y describe cómo definir correctamente los parámetros usando JSON Schema.

Cuando definimos herramientas para un agente de IA, debemos describir los parámetros usando JSON Schema. Esto permite que el modelo comprenda qué tipo de datos esperamos recibir. A continuación explicamos los tipos más comunes que utilizamos cuando configuramos nuestras propias funciones.

## 1. Tipos simples

Los usamos cuando el parámetro representa un único valor.

|Tipo JSON|Uso principal|Ejemplo de valor|
|---|---|---|
|`string`|Texto simple|`"archivo.md"`|
|`number`|Cualquier número|`12.5`|
|`boolean`|Estados activado/desactivado|`true`|

Ejemplo de definición:

```json
"directory": {
  "type": "string",
  "description": "Ruta donde vamos a crear los archivos"
}
```

## 2. Listas o arrays

Los usamos cuando el parámetro debe recibir varios elementos del mismo tipo.  
Un array siempre incluye la propiedad `items`, que indica el tipo de cada elemento.

```json
"filenames": {
  "type": "array",
  "items": { "type": "string" },
  "description": "Lista de nombres de archivo que queremos crear"
}
```

En este caso, el agente podría enviar algo como:

```json
["resumen.md", "notas.md", "tarea.md"]
```

## 3. Objetos

Los usamos cuando el parámetro representa un valor compuesto con varias propiedades internas.

```json
"metadata": {
  "type": "object",
  "properties": {
    "author": { "type": "string" },
    "version": { "type": "number" }
  }
}
```

En estos casos, el valor que recibe la herramienta tiene estructura interna, por ejemplo:

```json
{
  "author": "Metahumo",
  "version": 1.0
}
```

## Resumen general

|Tipo|Cuándo lo usamos|
|---|---|
|`string`|Cuando esperamos un único texto|
|`number`|Cuando necesitamos un valor numérico|
|`boolean`|Cuando queremos activar o desactivar algo|
|`array`|Cuando necesitamos recibir varios valores|
|`object`|Cuando el parámetro tiene varios subcampos|

Con esta clasificación podemos estructurar correctamente los parámetros de nuestras herramientas y el agente podrá saber qué datos debe generar o enviar según el contexto de la tarea.