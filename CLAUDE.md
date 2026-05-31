## Estado actual del MVP (actualizado)

**Completado:**
- Auth completo con creación de empresa en registro
- FAQs: CRUD completo con aislamiento por company_id
- Documentos: subida PDF, vectorización en Qdrant, listado y borrado
- Chat RAG: búsqueda en FAQs + documentos, umbral similitud 0.75,
  respuesta "no sé" si no supera umbral, fuentes visibles con nombre,
  confidence persistido en historial
- Tickets: modelo, endpoints POST/GET/PATCH, migración aplicada
- Chat crea ticket automático cuando confidence=0.0
- Rate limiting en POST /chat/messages — 20 req/min por user_id
- Rediseño visual frontend — tema premium dark (negro #0A0A0A / dorado #C9A84C)
- Error boundaries globales en frontend
- Ciclo completo de tickets:
  · TicketNote (tabla ticket_notes) — notas internas por admin
  · Ticket.resolution_message — mensaje al usuario al resolver
  · GET /tickets/my — tickets del usuario autenticado
  · Kanban admin con panel de detalle expandible (notas + resolución + crear FAQ)
  · Dashboard usuario: sección "Mis consultas escaladas" condicional
  · Sidebar usuario: "Mis Consultas" condicional con indicador de pendientes
  · Página /my-tickets — historial completo del usuario

**Próximo sprint (por orden):**
1. Notificaciones en tiempo real (WebSocket o polling) cuando un ticket cambia de estado
2. Búsqueda y filtros en el kanban (por status, priority, fecha, usuario)
3. Paginación en GET /tickets/ y GET /tickets/my
4. Tests de integración para el flujo ticket → resolución → FAQ
5. Exportar tickets resueltos a CSV

## Core del producto — arquitectura de roles

**Super Admin:** acceso total, system services (Qdrant/Ollama/PostgreSQL), gestión de usuarios y roles.
**Admin:** FAQs + documentos + tickets kanban con detalle (notas, resolución, crear FAQ). Sin acceso a system services.
**User:** solo chat. Ve sus tickets escalados en dashboard y /my-tickets. Recibe respuesta al resolver.

**Flujo de registro:**
1. Cualquiera se registra — queda en estado "pending"
2. Super Admin o Admin aprueba y asigna rol
3. Usuario aprobado accede según su rol

**Flujo de ticket completo:**
1. Chat detecta confidence=0.0 → crea ticket automáticamente
2. Admin ve ticket en kanban → añade notas internas → mueve a In Progress
3. Admin escribe resolution_message → resuelve → opcionalmente crea FAQ
4. Usuario ve "Respuesta del equipo" en dashboard y /my-tickets

**Regla clave:** nunca mezclar vistas entre roles. Cada rol ve exactamente lo que le corresponde.
