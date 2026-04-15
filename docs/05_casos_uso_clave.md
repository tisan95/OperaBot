# Casos de uso clave

## 1. FAQ sin chat

- El usuario entra al panel.
- Busca o navega por categorías de procedimientos.
- Abre una ficha que explica paso a paso cómo hacer algo.
- No necesita hablar con el chat.

## 2. Chat para duda concreta

- El usuario no tiene claro qué buscar.
- Abre el chat, describe su duda en lenguaje natural.
- OperaBot responde con pasos estructurados y muestra:
  - Origen de la información (manual, procedimiento, etc.).
  - Nivel de confianza aproximado.
  - Opción de “escalar” si no está seguro.

## 3. Admin revisando contenido

- El admin revisa qué preguntas se están haciendo y cómo se responden.
- Detecta lagunas en la documentación (consultas sin buena respuesta, temas recurrentes sin artículo).
- Edita o crea nuevos artículos de conocimiento.
- Marca qué artículos deben usarse como fuentes preferentes en ciertas respuestas.

## 4. Onboarding de un nuevo empleado

- El nuevo empleado accede a una sección de “primeros pasos”.
- Consulta FAQs específicas de onboarding.
- Usa el chat cuando algo no encaja con los documentos.

## 5. Admin convirtiendo insights en tareas (kanban)

- El admin entra al panel y ve estadísticas:
  - Temas más preguntados.
  - Respuestas peor valoradas.
  - Consultas sin buen match de contenido.
- Desde esa vista, selecciona un problema (p. ej. “Muchas dudas sobre procedimiento X”).
- Hace clic en “Crear tarea en kanban”.
- El sistema crea una tarjeta en el tablero kanban configurado con:
  - Título (ej. “Crear/actualizar manual de procedimiento X”).
  - Descripción (resumen de consultas + ejemplo de frases de usuarios).
  - Enlace al panel de OperaBot para más contexto.
