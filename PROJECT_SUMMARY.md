# PROJECT_SUMMARY_OperaBot

## Producto
OperaBot evoluciona desde un MVP de FAQs/chat hacia un SaaS multi-tenant más amplio, pero el núcleo operativo visible del repositorio sigue siendo autenticación de usuarios, gestión de FAQs, chat con LLM y un panel/admin básico.

## Stack
- Backend: FastAPI, SQLAlchemy, PostgreSQL, JWT, bcrypt, pytest.
- Frontend: Next.js (App Router), React, TypeScript, Tailwind CSS.
- Infra local: configuración guiada por `SETUP.md` y `docker-compose.yml`.

## Estado funcional resumido
- Registro, login y logout implementados.
- CRUD de FAQs al menos parcialmente implementado.
- Chat con integración LLM y persistencia de mensajes.
- Aislamiento multi-tenant basado en `company_id`.
- Tests backend unitarios e integración presentes y pasando según la auditoría.

## Deuda técnica ya identificada en la propia doc
- Migración a `ConfigDict` de Pydantic (quitar warnings).
- Implementar rate limiting en el endpoint de chat.
- Añadir error boundaries en el frontend.
- Añadir session timeout para las sesiones de usuario.

## Decisiones activas para continuar
- No reescribir la arquitectura existente.
- Priorizar pequeños desbloqueos que permitan avanzar features.
- Mantener los ADRs como memoria técnica en `reference/`, no como contexto base.
- Tratar la documentación generada por GitHub Agents (business, requirements, etc.) como histórico útil que solo se consulta cuando una tarea lo pida.