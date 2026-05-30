## Estado actual del MVP (actualizado)

**Completado:**
- Auth completo con creación de empresa en registro
- FAQs: CRUD completo con aislamiento por company_id
- Documentos: subida PDF, vectorización en Qdrant, listado y borrado
- Chat RAG: búsqueda en FAQs + documentos, umbral similitud 0.75,
  respuesta "no sé" si no supera umbral, fuentes visibles con nombre,
  confidence persistido en historial
- Tickets: modelo, endpoints POST/GET/PATCH, migración aplicada

**Próximo sprint (por orden):**
1. Conectar chat con tickets: cuando confidence=0.0 crear ticket automático
2. Frontend kanban: página /admin/tickets con vista por status y priority
3. Frontend tickets: que el usuario vea "tu pregunta ha sido escalada"
4. Rate limiting en endpoint de chat
5. Error boundaries en frontend

## Core del producto — arquitectura de roles

**Super Admin:** acceso total, system services (Qdrant/Ollama/PostgreSQL), gestión de usuarios y roles.
**Admin:** FAQs + documentos + tickets kanban. Sin acceso a system services.
**User:** solo chat. Puede crear tickets desde el chat si algo falla.

**Flujo de registro:**
1. Cualquiera se registra — queda en estado "pending"
2. Super Admin o Admin aprueba y asigna rol
3. Usuario aprobado accede según su rol

**Flujo de ticket desde chat:**
1. Usuario dice "no funciona" o "he seguido los pasos y no va"
2. El chat recoge los datos y crea el ticket automáticamente
3. Admin ve el ticket en el kanban y lo gestiona

**Regla clave:** nunca mezclar vistas entre roles. Cada rol ve exactamente lo que le corresponde.
