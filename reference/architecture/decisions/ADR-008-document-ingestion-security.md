# ADR-008: Document Ingestion Security and Text Extraction

**Status**: Accepted
**Date**: 2026-04-20
**Author**: Architect
**Scope**: MVP Document Ingestion

## Context and Problem Statement

OperaBot must allow companies to ingest knowledge documents safely so the chat assistant and FAQ search can use them. Document upload introduces security risk because files can contain hidden scripts, malformed content, or malicious payloads.

The architecture must decide how to accept documents, extract searchable content, and store metadata without exposing the system or users to unsafe data.

## Decision Drivers

1. **Security**: Prevent malicious uploads and reduce attack surface
2. **Maintainability**: Keep ingestion logic simple for MVP
3. **Trustworthiness**: Ensure extracted content is clean and searchable
4. **Performance**: Support upload processing without blocking the chat pipeline
5. **Compliance**: Restrict document formats and minimize unsafe file handling

## Considered Options

### Option 1: Store raw files and index later

Pros:
- Keeps original files intact
- Enables rich file retrieval later

Cons:
- Increased attack surface
- Requires robust storage and scanning
- Delays search until indexing completes
- Increases complexity for MVP

### Option 2: Validate and extract text on upload (CHOSEN)

Pros:
- Reduces risk by only storing sanitized text and metadata
- Enables immediate search and vectorization
- Simpler for MVP implementation
- Easier to validate allowed file types and sizes

Cons:
- Loses original binary file fidelity
- Requires reliable text extraction for supported formats
- May require more integration effort for PDF / DOCX parsing

### Option 3: Offload ingestion to a managed service

Pros:
- Outsources parsing and scanning responsibility
- Can provide built-in security and content extraction

Cons:
- Additional external dependency for MVP
- Increased cost and integration complexity
- Less control over ingestion behavior

## Decision Outcome

**Choose: Validate and extract text on upload**.

The MVP will support a limited set of document formats and perform safe extraction to plain text. The system will store extracted text and metadata in PostgreSQL and use Qdrant for vector embeddings. Raw file storage is deferred until a future phase.

### Implementation guidance

- Accept only whitelisted file types such as `.txt`, `.md`, `.pdf`, `.docx`
- Enforce maximum upload size (for example 5 MB for MVP)
- Use a safe extraction pipeline:
  - plain text files: read with UTF-8 fallback
  - PDFs: extract text with a safe parser such as `pdfplumber` or `pypdf`
  - DOCX: extract text with `python-docx`
- Sanitize extracted text to remove control characters and invisible content
- Reject any upload that fails extraction or exceeds limits
- Do not execute or render uploaded files on the server
- Generate vector embeddings after extraction and store them in Qdrant

## Consequences

### Good
- Reduces attack surface by avoiding raw binary storage
- Provides searchable content immediately for the RAG pipeline
- Keeps MVP ingestion logic constrained and auditable
- Aligns with security constraints from the requirements handoff

### Bad
- Original documents are not preserved in their raw format for future use
- Some complex content may lose formatting or structure during extraction
- Extraction failures may require strict error handling and user feedback

## Research Links

- https://owasp.org/www-project-top-ten/ — File upload security risks
- https://docs.python.org/3/library/io.html — Safe file reading patterns
- https://pypi.org/project/pdfplumber/ — PDF text extraction
- https://python-docx.readthedocs.io/ — DOCX parsing for Python
