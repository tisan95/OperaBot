## Estado actual del MVP

### Completado

**Infraestructura base**
- Auth completo con creación de empresa en registro
- Multi-tenant: aislamiento por company_id en todas las queries
- Roles: super_admin / admin / user con vistas separadas
- Rate limiting en POST /chat/messages (20 req/min por user_id)
- Error boundaries globales en frontend

**Conocimiento (RAG)**
- FAQs: CRUD completo con editor rico TipTap (negritas, listas, tablas, links, código)
- Documentos: subida PDF, almacenamiento persistente en disco, vectorización en Qdrant
- RAG: búsqueda en FAQs + documentos, umbral similitud 0.60, confidence persistido
- Editor rico en notas de ticket y resolución (mismo componente TipTap)
- Sanitización HTML en frontend (sanitizeHtml helper)

**Chat conversacional**
- Clasificador de intención: GREETING / CONFIRMATION / NEGATION / QUESTION
- GREETING/CONFIRMATION/NEGATION → respuestas instantáneas sin RAG ni Ollama
- QUESTION → RAG → ui_hint: resolution_prompt (con docs) o escalate_prompt (sin docs)
- Follow-up proactivo tras 3+ intercambios RAG sin resolución
- Visor PDF inline: cuando el bot cita un doc, aparece tarjeta [Ver] [Descargar]
  - Preview: fetch con credentials → Blob → iframe (sin exponer URL real)
  - Descargar: solo admin/super_admin
  - USER solo puede previsualizar, no descargar

**Escalado inteligente**
- Botones [Sí, resuelto] / [No me ha servido] en respuestas RAG
- Flujo de 2 pasos: Ollama analiza la conversación y genera 2 preguntas específicas
  según el tipo de problema detectado antes de crear el ticket
- Fallback determinista si Ollama falla
- POST /chat/escalate crea ticket con: resumen del problema + historial + respuestas del usuario

**Tickets**
- Modelo: Ticket + TicketNote, campo resolution_message
- Kanban admin: Open / In Progress / Resolved
- Panel de detalle clickable: notas internas (rich text), resolución (rich text), checkbox crear FAQ
- GET /tickets/my para usuarios: historial completo con respuesta del equipo
- Dashboard usuario: sección "Mis consultas escaladas" condicional
- Sidebar usuario: "Mis Consultas" aparece solo si hay tickets, punto dorado si hay pendientes
- Página /my-tickets: historial completo, resolution_message renderizado como HTML rico

**Backend endpoints relevantes**
- POST /chat/messages — clasificación intención + RAG + cited_documents
- POST /chat/escalate-questions — genera preguntas contextuales con Ollama
- POST /chat/escalate — crea ticket enriquecido
- GET /documents/{id}/preview — cualquier usuario autenticado, inline
- GET /documents/{id}/download — solo admin/super_admin, attachment
- GET /tickets/my — tickets del usuario autenticado
- POST/GET /tickets/{id}/notes — notas internas admin

---

## Arquitectura de negocio

**Modelo SaaS:**
- Producción: API externa (Groq o Anthropic) — coste por token, sin infraestructura LLM
- Demo/desarrollo: Ollama local, sin coste
- On-premise: solo bajo demanda como proyecto custom Enterprise

**LLM provider:** configurable via LLM_PROVIDER en .env (ollama / groq / anthropic)
**Email:** SMTP local MailHog en desarrollo, Resend en producción (EMAIL_PROVIDER en .env)

---

## Arquitectura de roles

**Super Admin:** sistema completo — Qdrant/Ollama/PostgreSQL, usuarios, todas las empresas
**Admin:** FAQs + documentos + kanban de tickets (notas, resolución, crear FAQ)
**User:** chat + ver sus tickets escalados + previsualizar PDFs citados

**Flujo de registro:**
1. Usuario se registra → estado "pending"
2. Super Admin o Admin aprueba y asigna rol
3. Usuario aprobado accede según su rol

**Flujo de ticket (ciclo completo):**
1. Chat devuelve respuesta RAG → usuario pulsa "No me ha servido"
2. Ollama analiza conversación → genera 2 preguntas específicas al problema
3. Usuario responde → POST /chat/escalate crea ticket con contexto completo
4. Admin ve ticket en kanban → añade notas internas → mueve a In Progress
5. Admin escribe resolution_message (rich text) → resuelve → opcionalmente crea FAQ
6. Usuario ve "Respuesta del equipo" (HTML rico) en dashboard y /my-tickets

**Regla clave:** nunca mezclar vistas entre roles.

---

## Próximo sprint (orden estricto)

1. **Tests automáticos backend** — pytest, sin necesidad de login manual
2. **Archivado automático tickets resueltos** — lógica backend + decisión usuario en UI
3. **Abstracción LLM provider** — variable LLM_PROVIDER en .env,
   soportar ollama/groq/anthropic sin cambiar código
4. **Email transaccional** — MailHog local, Resend producción,
   variable EMAIL_PROVIDER en .env

## Sprint siguiente (multi-tenant real)

1. Página pública de registro de empresa (onboarding)
2. Sistema de invitaciones por email — admin invita usuarios de su empresa
3. Panel superadmin OperaBot — ver todas las empresas, trials, activar/desactivar
4. Límites por plan — usuarios, documentos, consultas según tier contratado

## Sprint futuro (cuando haya tracción)

1. Web de presentación con trial gratuito
2. Integración Stripe para pagos
3. Switch Ollama → Groq/Resend para producción real

---

## Instrucciones para Claude Code

- Lee solo los archivos relevantes para la tarea concreta
- Antes de implementar, describe en 3 líneas qué vas a hacer
- Commits atómicos por feature
- Si algo funciona, no lo toques
- Pregunta antes de instalar dependencias nuevas
- Variables de entorno sensibles siempre en .env, nunca hardcodeadas
- No añadir comentarios obvios — solo WHY no-obvios
- No crear tests si no se piden explícitamente
