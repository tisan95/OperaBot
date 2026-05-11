# CLAUDE.md

## Project
OperaBot = SaaS multi-tenant de FAQs + chat para empresas.
Stack principal: FastAPI + PostgreSQL en backend, Next.js + TypeScript + Tailwind en frontend.
Hay decisiones previas de vector store, integración LLM y patrón RAG; revísalas solo cuando la tarea toque retrieval, chat o memoria.

## Read order
1. `PROJECT_SUMMARY.md`
2. `SETUP.md`
3. Archivos exactos implicados en la tarea en `backend/` o `frontend/`
4. ADRs técnicos relevantes en `reference/architecture/decisions`
5. Roadmap/auditoría en `reference/` solo para priorizar, no para implementar por defecto

## Ignore by default
- `archive/`
- `.github/` (especialmente agents, chatmodes, instructions, templates si existen)
- `archive/business-context/` (vision, mercado, personas, etc.)
- `_devprocess/` salvo que se solicite explícitamente más contexto de arquitectura
- Cualquier `.log` o scripts de debug en `archive/debug/`

## Work rules
- Haz cambios mínimos y locales sobre el código existente.
- No cargues el repositorio entero en contexto.
- No uses documentación histórica como contexto base salvo que te lo pida expresamente.
- Si la tarea toca chat o memoria, revisa antes los ADR de vector store y RAG en `reference/architecture/decisions`.
- Siempre termina con pasos de validación concretos (por ejemplo, qué tests o comandos ejecutar).

## Output style
- Sé técnico y directo.
- Usa listas de pasos cuando haya varias acciones.
- Marca claramente tus supuestos cuando falte contexto.
- Separa siempre: diagnóstico, plan, implementación sugerida y validación.