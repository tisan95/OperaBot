# ADR-002: Vectorization Failure Handling for FAQ Creation

**Status:** Proposed
**Date:** 2026-04-23
**Deciders:** Architect, Tech Lead

## Context

FEATURE-005 (Convert Escalation to FAQ) creates a new FAQ entry and immediately vectorizes it for RAG searchability. The vectorization process involves:

1. Generate embeddings using nomic-embed-text model
2. Store vectors in Qdrant vector database
3. Create searchable FAQ record

If Qdrant fails during vectorization, we face two problems:
- FAQ is created but unsearchable (data exists but not discoverable)
- User sees error, loses confidence in admin tool
- No mechanism to retry vectorization later

Current system already uses Qdrant for document vectorization. Escalation-to-FAQ conversion should handle failures gracefully without losing data.

**Triggering ASR:**
- CRITICAL: Vectorization Robustness (FEATURE-005)
- Quality Attribute: Reliability (System doesn't lose data on component failure)

## Decision Drivers

- **Reliability**: FAQ creation must succeed even if Qdrant is temporarily unavailable. Users cannot lose work.
- **User Experience**: Admin should know immediately if FAQ is created but not yet searchable (transparent status).
- **Recovery**: System must have a way to retry vectorization without manual intervention.
- **Scalability**: Vectorization can be slow. Admin shouldn't wait for Qdrant to respond before escalation is resolved.
- **Data Integrity**: FAQ and vector data must remain consistent (no orphaned FAQs or stale vectors).

## Considered Options

### Option 1: Synchronous Vectorization (Blocking)

Escalation-to-FAQ flow waits for vectorization to complete before returning success. If Qdrant fails, entire operation fails and is retried by user.

```
User action: "Convert to FAQ"
  -> Create FAQ in DB
  -> Generate embeddings (slow, blocks)
  -> Store vectors in Qdrant
  -> Return success/failure
```

- Pro: Simple, no async complexity
- Pro: Admin immediately knows if FAQ is searchable
- Pro: Strong consistency (FAQ and vectors are always in sync)
- Con: Slow user experience (Qdrant latency adds to operation)
- Con: If Qdrant fails, admin must retry entire operation
- Con: Vectorization bottleneck for admins managing many escalations
- Con: Blocks other API operations

### Option 2: Asynchronous Vectorization with Queue

FAQ created immediately, vectorization happens asynchronously via background job queue (Celery/RQ). Admin sees "FAQ created, vectorization pending" status.

```
User action: "Convert to FAQ"
  -> Create FAQ in DB (fast)
  -> Enqueue vectorization task
  -> Return success immediately
  [Background job later]:
  -> Generate embeddings
  -> Store vectors in Qdrant
  -> Update FAQ status to "searchable"
```

- Pro: Excellent UX (admin gets immediate feedback)
- Pro: Non-blocking (admin can continue managing escalations)
- Pro: Natural retry mechanism (job queue handles retries)
- Pro: Scales well (vectorization happens in background)
- Pro: Failure is transparent (admin can see FAQ status)
- Con: Requires job queue infrastructure (Celery or RQ)
- Con: FAQ is created but not immediately searchable
- Con: Eventual consistency (small gap between FAQ creation and searchability)
- Con: Complex error recovery (need dead-letter queue for failed jobs)

### Option 3: Hybrid Approach (Optimistic Async with Fallback)

Try synchronous vectorization first (fast path). If it takes >500ms, offload to background job and return "pending searchability" status.

```
User action: "Convert to FAQ"
  -> Create FAQ in DB
  -> Start vectorization with timeout (500ms)
    If completes in time:
      -> Return "FAQ created and searchable"
    If timeout:
      -> Enqueue background job
      -> Return "FAQ created, vectorization pending"
```

- Pro: Fast path for normal cases (immediate searchability)
- Pro: Fallback to async if slow (no blocking)
- Pro: User gets either "ready now" or "pending" status
- Con: Adds latency tracking complexity
- Con: Still requires background job infrastructure
- Con: Error handling is more complex (handle both sync and async failures)

## Decision

**Proposed Option:** Option 2 (Asynchronous Vectorization with Queue)

**Rationale:**

FAQ vectorization is not on the critical path for admin workflow. An admin resolving an escalation primarily needs to (1) record the answer, (2) know the FAQ is created. Whether the FAQ becomes searchable immediately or in the next 10 seconds is secondary.

Option 2 provides:
- Excellent user experience (instant feedback, no blocking)
- Natural failure recovery (job queue handles retries)
- Scalability (batch vectorization during off-peak hours if needed)
- Transparency (admin can query FAQ status and see "vectorization pending")

Rationale for rejecting Option 1: Synchronous vectorization is too slow and blocks critical operations. Qdrant latency can add 1-5 seconds to the operation, which compounds when admins create multiple FAQs.

Rationale for rejecting Option 3: Hybrid approach adds complexity without significant benefit. Since we're already building async infrastructure for Option 2, Option 3's "fast path" optimization is premature.

**Implementation approach:**
1. Use existing project task queue (check whether Celery is installed, otherwise use RQ)
2. Create task: `vectorize_faq(faq_id, company_id)`
3. Enqueue task in FEATURE-005 endpoint, return immediately
4. Task retries automatically on failure (up to 3 times)
5. Add `vectorization_status` field to FAQ model: "pending" or "complete"
6. Dashboard shows FAQ with "searchable" or "pending" indicator

## Consequences

### Positive
- Admin gets immediate feedback, no blocking
- Job queue provides built-in retry mechanism
- Failure is transparent (admin can see which FAQs are pending vectorization)
- Natural retry: failed jobs stay in queue for retries
- Admin can batch-process escalations quickly

### Negative
- FAQ is created but not immediately searchable
- Requires job queue infrastructure (Celery or RQ)
- Dead-letter queue needed for jobs that fail after 3 retries
- Slightly more complex error handling and status tracking
- Admin must understand "pending" state

### Risks
- **Risk: Job queue infrastructure not available** - Mitigation: Use in-memory queue for simple cases (RQ with Redis is light), upgrade to Celery only if needed
- **Risk: FAQ is created but vectorization task is lost** - Mitigation: Store task ID in FAQ record, implement dead-letter monitoring
- **Risk: Stale FAQ status (marked complete but actually failed)** - Mitigation: Verify vectors exist in Qdrant before marking complete
- **Risk: Job queue message queue floods if vectorization is too slow** - Mitigation: Monitor queue depth, tune vectorization batch size

## Implementation Notes

- Check current OperaBot infrastructure for existing task queue (Celery/RQ)
- If none exists, use RQ with Redis (simple, light-weight)
- Create Celery task or RQ job:
  ```python
  @celery.task(bind=True, max_retries=3)
  def vectorize_faq(self, faq_id: int, company_id: int):
      # Generate embeddings
      # Store in Qdrant
      # Update FAQ.vectorization_status = "complete"
  ```
- Add to FAQ model:
  ```python
  vectorization_status: str = "pending"  # pending | complete | failed
  last_vectorization_error: Optional[str] = None
  ```
- In FEATURE-005 endpoint:
  ```python
  faq = create_faq(...)
  vectorize_faq.delay(faq.id, current_company_id)
  return {"status": "created", "vectorization": "pending"}
  ```
- Add monitoring: Alert if vectorization queue depth exceeds threshold

## Related Decisions

- ADR-001: Multi-Tenancy Data Isolation (company_id filtering applies to vectorization too)
- FEATURE-005: Convert Escalation to FAQ (implements this ADR)
- Potential future: ADR on Qdrant failover/replication strategy

## References

- Celery Task Queue: https://docs.celeryproject.org/
- RQ (Redis Queue): https://python-rq.org/
- Idempotent Task Design: https://docs.celeryproject.org/en/stable/tutorials/tasks.html#tips-and-best-practices
