# Power Automate - Guías y Casos Prácticos

Documentación detallada sobre Power Automate, incluyendo conceptos fundamentales, buenas prácticas y casos prácticos paso a paso para automatizar tareas en Microsoft 365.

## Contenido

Esta sección contiene:

1. **Introducción a Power Automate**: Conceptos básicos, funcionamiento y mejores prácticas
2. **Casos Prácticos**: Guías detalladas con capturas de pantalla para implementar automatizaciones reales

## ¿Qué es Power Automate?

Power Automate es una herramienta de Microsoft diseñada para automatizar tareas y flujos de trabajo entre diferentes aplicaciones y servicios dentro del ecosistema de Microsoft 365. Permite:

-  Eliminar tareas repetitivas
-  Optimizar procesos internos
-  Reducir errores humanos
-  Aumentar la eficiencia y productividad

## Documentación disponible

### 01. Introducción a Power Automate

Conceptos fundamentales para comenzar a trabajar con Power Automate:

- Qué es y para qué sirve
- Ubicación dentro del ecosistema Microsoft 365
- Cómo se utiliza (proceso básico)
- Conceptos clave: Triggers, Actions, Conectores, Flows
- Tips y buenas prácticas

[Ver documento completo](./01.%20Introducción%20a%20Power%20Automate.md)

### 02. Caso Práctico - Obtener archivo adjunto de mail en OneDrive

Guía práctica paso a paso para crear tu primera automatización:

**Objetivo**: Automatizar la descarga de archivos adjuntos recibidos por correo electrónico y su almacenamiento en OneDrive

**Aprenderás a**:
- Configurar un desencadenador (trigger) de correo electrónico
- Filtrar correos por remitente, importancia y presencia de adjuntos
- Procesar múltiples adjuntos automáticamente
- Guardar archivos en carpetas específicas de OneDrive
- Probar y activar el flujo

**Incluye**: Capturas de pantalla detalladas de cada paso del proceso

[Ver guía completa](./02.%20Caso%20práctico%20-%20Obtener%20archivo%20%20adjunto%20de%20mail%20en%20OneDrive.md)

## Conceptos clave

| Concepto | Descripción |
|----------|-------------|
| **Trigger / Disparador** | Evento que inicia el flujo de trabajo |
| **Action / Acción** | Tarea que se ejecuta después del trigger |
| **Conectores** | Elementos que conectan diferentes aplicaciones |
| **Flow / Flujo** | Secuencia completa de disparadores y acciones |
| **Run / Ejecución** | Instancia específica de un flujo en ejecución |

## Proceso básico de trabajo

1. **Elegir un trigger**: Seleccionar el evento que inicia el flujo
2. **Definir acciones**: Establecer las tareas a ejecutar
3. **Configurar conectores**: Conectar las aplicaciones necesarias
4. **Probar el flujo**: Verificar el funcionamiento correcto
5. **Publicar y ejecutar**: Activar el flujo para uso en producción

## Buenas prácticas

-  Planificar bien los flujos antes de crearlos
-  Revisar los permisos de cada aplicación y conector
-  Testear con datos de prueba antes del despliegue
-  Documentar la finalidad de cada flujo
-  Usar siempre cuentas corporativas autorizadas
-  Revisar periódicamente los flujos activos
-  Desactivar flujos que ya no sean necesarios

## Estructura de archivos

```
Power_Automate/
├── README.md
├── 01. Introducción a Power Automate.md
├── 02. Caso práctico - Obtener archivo adjunto de mail en OneDrive.md
└── Images/
    └── (capturas de pantalla de los tutoriales)
```

## Casos de uso comunes

Power Automate es ideal para automatizar:

-  Procesamiento automático de correos electrónicos
-  Organización de documentos y archivos
-  Envío de notificaciones y recordatorios
-  Actualización de bases de datos y listas
-  Coordinación entre equipos en Teams
-  Procesamiento de respuestas de Forms
-  Gestión de eventos y reuniones

## Recursos adicionales

- [Documentación oficial de Power Automate](https://learn.microsoft.com/power-automate/)
- [Microsoft Learn: Cursos de Power Automate](https://learn.microsoft.com/training/power-automate/)
- [Power Automate Community](https://powerusers.microsoft.com/t5/Microsoft-Power-Automate/ct-p/MPACommunity)

## Próximos pasos

1. Lee la introducción para familiarizarte con los conceptos
2. Sigue el caso práctico paso a paso
3. Experimenta creando tus propios flujos
4. Explora conectores adicionales según tus necesidades

---

**Nota**: Asegúrate de tener acceso a una cuenta de Microsoft 365 corporativa para poder crear y ejecutar flujos de Power Automate.

---
