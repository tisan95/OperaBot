# MVP y arquitectura a alto nivel

## MVP funcional

El MVP de OperaBot debería incluir:

- Un **módulo de autenticación** básica (usuarios y admins).
- Un **panel de usuario** con:
  - Acceso a un chat para preguntar dudas.
  - Acceso a una FAQ / buscador de manuales sin usar el chat.
- Un **panel de admin** con:
  - Gestión de artículos de conocimiento / FAQs.
  - Revisión de respuestas de la IA, posibilidad de corregir y mejorar.
  - Subida/actualización de manuales y documentación fuente.
  - Acceso a estadísticas básicas de uso (qué se pregunta, qué no se responde bien, qué falta).
  - Integración con un tablero kanban externo para convertir hallazgos en tareas de mejora.

## Integración con kanban externo

Para dar poder de decisión al admin, el sistema se conectará con una herramienta de kanban gratuita (por ejemplo, Trello, Jira free, Linear free o similar). La idea es:

- Desde el panel admin, poder crear tareas en el tablero cuando se detecten:
  - Lagunas de documentación.
  - Respuestas con baja valoración.
  - Nuevas necesidades detectadas en las consultas.
- Las tareas se gestionan en el tablero externo (priorización, asignación, seguimiento), pero se crean y se vinculan desde OperaBot.

Un primer paso viable para el MVP:

- Botón “Crear tarea en kanban” en ciertos insights.
- Llamada a la API del kanban para crear la tarjeta con:
  - Título (ej. “Crear manual sobre X”).
  - Descripción (contexto y ejemplos de preguntas).
  - Enlace al listado de consultas relacionadas.

## Componentes de arquitectura (alta nivel)

- **Frontend web**:
  - Panel usuario (chat + FAQ).
  - Panel admin (gestión de contenido + vista de estadísticas básicas + acciones de creación de tareas en kanban).

- **Backend / API**:
  - Autenticación y roles.
  - Gestión de artículos de conocimiento.
  - Endpoint de chat que orquesta la llamada al LLM y recupera contexto de la base de conocimiento.
  - Endpoints para estadísticas (consultas por tipo, valoraciones, lagunas detectadas).
  - Conector con API de la herramienta kanban elegida.

- **Motor de IA**:
  - LLM externo o interno.
  - Capa de recuperación de contexto (vector DB o similar) desde la documentación de la empresa.

- **Base de conocimiento**:
  - Documentos internos (PDFs, manuales, procedimientos).
  - Artículos estructurados tipo FAQ.
  - Metadatos que permitan relacionar consultas con artículos y detectar huecos.

Esta arquitectura es un punto de partida para el agente de `/architecture`, no un diseño definitivo.
