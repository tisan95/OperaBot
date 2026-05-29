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
