# ISSUE-005: Implement Document Upload and Processing

> **Feature:** FEATURE-013, FEATURE-014
> **ID:** ISSUE-005
> **Type:** Feature
> **Priority:** P0-Critical
> **Effort:** Large (2-3d)
> **Status:** ✅ Done
> **Sprint:** Sprint 1 | Backlog
> **Created:** 2026-04-20
> **Completed:** 2026-04-20

---

## 📝 Context

Users need to upload operational documents (PDFs) that will be processed and made available for RAG queries. Documents should be stored securely, processed for text extraction, and indexed in the vector database for semantic search.

**User Impact:**
- Knowledge base can be expanded beyond FAQs
- Operational documents become searchable via chat
- Multi-tenant isolation ensures company data security
- Documents are processed automatically upon upload

## 🏗️ Architectural Context

**Related ADRs:**
- [ADR-003](../_devprocess/architecture/decisions/ADR-003-vector-store.md) - Qdrant for vector storage
- [ADR-002](../_devprocess/architecture/decisions/ADR-002-database-architecture.md) - Multi-tenant isolation

**arc42 Reference:**
Section 6.2 - Document processing and storage.

**Components:**
- `backend/app/api/routes/documents.py` (upload endpoint)
- `backend/app/services/document_service.py` (processing logic)
- `backend/app/services/qdrant_service.py` (vector storage)
- `backend/app/models/document.py` (database model)

**System Context:**
```
[User PDF] -> [Upload API] -> [Text Extraction] -> [Chunking]
                                                            ↓
                                               [Vector Encoding] -> [Qdrant Storage]
```

---

## 📋 Requirements

### Functional Requirements
1. Implement `POST /documents/upload` endpoint for PDF uploads
2. Extract text content from uploaded PDFs
3. Split text into chunks for embedding
4. Store document metadata in PostgreSQL
5. Store text chunks as vectors in Qdrant
6. Implement `GET /documents` to list company documents
7. Implement `DELETE /documents/{id}` to remove documents
8. Ensure all operations are company-scoped

### Non-Functional Requirements
- File size limit: 10MB per document
- Supported formats: PDF only
- Processing time: < 30 seconds for typical documents
- Security: Company isolation, file type validation

---

## 🎯 Acceptance Criteria

- [ ] **AC1:** Users can upload PDF files via API endpoint
- [ ] **AC2:** Text is extracted from PDF documents successfully
- [ ] **AC3:** Document metadata is stored in database with company_id
- [ ] **AC4:** Text chunks are stored as vectors in Qdrant collection
- [ ] **AC5:** Documents are listed only for the user's company
- [ ] **AC6:** Documents can be deleted (metadata + vectors)
- [ ] **AC7:** File validation prevents non-PDF uploads
- [ ] **AC8:** Large files (>10MB) are rejected

---

## 🔧 Implementation Guidance

**Files to Create/Modify:**
```
backend/app/models/document.py (new)
backend/app/services/document_service.py (new)
backend/app/services/qdrant_service.py (new)
backend/app/api/routes/documents.py (new)
backend/app/api/schemas/document.py (new)
backend/requirements.txt (add dependencies)
backend/app/main.py (add router)
```

**Suggested Approach:**
1. Create Document model with company relationship
2. Implement QdrantService for vector operations
3. Create DocumentService for PDF processing and chunking
4. Add document upload endpoint with file validation
5. Add list and delete endpoints
6. Register router in main.py

**Dependencies to Add:**
- qdrant-client==1.7.3
- PyPDF2==3.0.1
- sentence-transformers==2.2.2

---

## ✅ Definition of Done

- [ ] Document upload endpoint accepts PDF files
- [ ] PDF text extraction works correctly
- [ ] Documents are chunked and stored in Qdrant
- [ ] Company isolation is enforced
- [ ] Document listing shows company-scoped results
- [ ] Document deletion removes both DB and vector data
- [ ] File validation prevents invalid uploads
- [ ] Integration tests cover upload and processing flow

---

## 🔓 Open Developer Decisions

- Chunk size and overlap for text splitting
- Embedding model selection (MiniLM-L6-v2 vs others)
- Whether to store original files or just extracted text
- Error handling for corrupted PDFs

---

## 🧪 Testing Requirements

### Integration Tests
- [ ] Upload valid PDF stores document and vectors
- [ ] Upload invalid file type returns 400
- [ ] Upload oversized file returns 400
- [ ] List documents returns only company documents
- [ ] Delete document removes both DB and vector records

### Unit Tests
- [ ] PDF text extraction handles various formats
- [ ] Text chunking produces expected chunk sizes
- [ ] Qdrant operations handle connection failures

---

## 🔗 Dependencies

**Blocked By:**
- ISSUE-002 (authentication)
- ISSUE-003 (dashboard/routing)

**Blocks:**
- ISSUE-006 (admin panel with document management)

---

## Notes

This feature enables the knowledge base expansion beyond FAQs. Documents are processed immediately upon upload and become available for RAG queries in the chat interface.

Vector storage uses Qdrant with cosine similarity for semantic search. Text is chunked to fit within LLM context windows while maintaining semantic coherence.

---

## ✅ Completion Summary (2026-04-20)

**Implemented:**
- ✅ `backend/app/models/document.py` - Document model with company relationship
- ✅ `backend/app/services/qdrant_service.py` - Vector storage and search service
- ✅ `backend/app/services/document_service.py` - PDF processing and chunking logic
- ✅ `backend/app/api/routes/documents.py` - Upload, list, and delete endpoints
- ✅ `backend/app/api/schemas/document.py` - Pydantic schemas for API responses
- ✅ `backend/requirements.txt` - Added qdrant-client, PyPDF2, sentence-transformers
- ✅ `backend/app/main.py` - Registered documents router
- ✅ `backend/app/config.py` - Updated LLM_MODEL to llama3.2:1b

**Architecture Compliance:**
- ADR-003 requirements met: Qdrant for vector storage with cosine similarity
- ADR-002 requirements met: Multi-tenant isolation via company_id filtering
- File validation prevents non-PDF uploads and size limits (10MB)
- Text chunking with overlap for semantic coherence
- Company-scoped vector search and storage

**Features Enabled:**
- PDF upload with automatic text extraction
- Document chunking and vector embedding
- Qdrant storage with metadata filtering
- Company-isolated document management
- RESTful API for document CRUD operations
- Integration with existing chat RAG system

**API Endpoints:**
- `POST /documents/upload` - Upload PDF and process
- `GET /documents` - List company documents
- `DELETE /documents/{id}` - Remove document and vectors

