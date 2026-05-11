# ISSUE-001: Fix Local Ollama Chat Integration and Prevent Generic Fallback

> **Feature:** FEATURE-008, FEATURE-009
> **ID:** ISSUE-001
> **Type:** Bug Fix
> **Priority:** P0-Critical
> **Effort:** Small (4-8h)
> **Status:** ✅ Done
> **Sprint:** Sprint 1 | Backlog
> **Created:** 2026-04-17

---

## 📝 Context

The chat path currently falls back to a generic answer when Ollama is enabled, which blocks the core real-time Q&A experience. This issue resolves the local LLM integration path so the chat endpoint returns actual Ollama responses while preserving the safe fallback behavior for provider failures.

**Contribution to Feature:**
Resolves FEATURE-008 and FEATURE-009 by making the chat service reliably deliver contextual answers from the configured LLM provider.

**User Impact:**
End users will receive meaningful chat responses instead of placeholder text, enabling the MVP chat experience and preserving trust.

---

## 🏗️ Architectural Context

**Related ADRs:**
- [ADR-004](../_devprocess/architecture/decisions/ADR-004-llm-integration.md) - LLM provider abstraction and fallback strategy
- [ADR-007](../_devprocess/architecture/decisions/ADR-007-rag-pattern.md) - Retrieval-augmented generation and prompt composition

**arc42 Reference:**
Section 4.3 - Runtime behavior for external LLM services and fallback handling.

**Architectural Decision Summary:**
> We use an asynchronous LLM client abstraction supporting Gemini and Ollama. This issue ensures the Ollama path returns parsed answers and only falls back when the provider is unreachable or returns invalid data.

**Component:**
LLM Integration Service (`backend/app/services/llm_client.py`) and Chat API (`backend/app/api/routes/chat.py`)

**System Context:**
```
[Chat API] -> [LLM Client] -> [Ollama / Gemini] 
                     ↓
                 [Fallback Response]
```

---

## 📋 Requirements

### Functional Requirements

1. Ensure `backend/app/services/llm_client.py` correctly sends requests to Ollama when `LLM_PROVIDER=ollama`.
2. Parse the Ollama response payload and return the generated answer text to the chat endpoint.
3. Preserve the existing Gemini support path unchanged.
4. Keep the safe fallback message path active only for real provider failures or invalid responses.
5. Add regression tests for both Ollama success and failure conditions.

### Non-Functional Requirements

- Performance: chat response must remain within the <5 second SLA target for provider round-trips.
- Security: do not expose API keys or provider internals through the chat response.

---

## 🎯 Acceptance Criteria

- [ ] **AC1:** `/chat/messages` returns a real answer when Ollama responds successfully.
  - Verification: integration or unit test mocking Ollama returns a valid answer payload.
- [ ] **AC2:** The endpoint still returns the configured fallback text when Ollama fails or returns invalid data.
  - Verification: tests cover network error, non-200 status, and malformed response.
- [ ] **AC3:** Gemini provider behavior remains unchanged and still functions when `LLM_PROVIDER=gemini`.
  - Verification: tests verify the Gemini code path is intact.
- [x] **AC4:** The new code is covered by unit tests in `backend/tests/unit/`.

---

## 🔧 Implementation Guidance

**Files to Create/Modify:**
```
backend/app/services/llm_client.py
backend/app/api/routes/chat.py
backend/tests/unit/test_llm_client.py
backend/tests/integration/test_chat_flow.py
```

**Suggested Approach:**
1. Add a focused unit test for `llm_client._generate_with_ollama()` success and failure cases.
2. Ensure `generate_answer()` returns provider text directly and only uses fallback on exceptions or malformed output.
3. Keep the existing `chat.py` endpoint logic stable and verify it forwards the final answer.

**Key Patterns/Standards:**
- Follow the async HTTP client pattern already used in the service layer.
- Do not introduce synchronous I/O in the request path.
- Keep provider-specific parsing inside `llm_client.py`.

---

## 🔒 Architectural Constraints (Non-Negotiable!)

**MUST:**
- Use the existing async service abstraction in `backend/app/services/llm_client.py`.
- Support both `LLM_PROVIDER=ollama` and `LLM_PROVIDER=gemini` without regression.
- Return the provider answer only after successful validation of the response payload.
- Preserve the fallback path for provider errors.

**MUST NOT:**
- Hardcode sensitive provider secrets or endpoint URLs in code.
- Remove or weaken the fallback safety mechanism.
- Introduce synchronous external calls in the chat request path.

---

## 🔓 Open for Developer Decision

- How to structure unit and integration tests for the LLM client.
- The exact response parsing implementation for Ollama payloads.
- Logging detail level for provider errors.
- Whether to add a dedicated `OllamaClient` helper class or keep it within `llm_client.py`.

---

## 🧪 Testing Requirements

### Unit Tests (PFLICHT)
- [ ] Test successful Ollama response parsing.
- [ ] Test failure handling for network errors.
- [ ] Test fallback behavior for invalid response payloads.
- [ ] Test that the Gemini path still resolves correctly.

### Integration Tests (falls relevant)
- [ ] Add or update chat endpoint coverage to assert the final answer payload.

### Minimum Coverage
- 80% coverage for the new `llm_client` code.

---

## ✅ Definition of Done

- [ ] Code updated to parse and return valid Ollama answers.
- [ ] Existing Gemini path remains functional.
- [ ] Regression tests added and passing.
- [ ] Fallback behavior preserved and tested.
- [ ] No new synchronous calls introduced.
- [ ] Documentation or inline comments updated as needed.

---

## 🔗 Dependencies

**Blocked By:**
- None

**Blocks:**
- [ISSUE-002](./ISSUE-002-*.md) - Next chat improvement or admin/analytics support

**Related:**
- [ADR-004](../_devprocess/architecture/decisions/ADR-004-llm-integration.md)
- [ADR-007](../_devprocess/architecture/decisions/ADR-007-rag-pattern.md)

---

## 💡 Notes for Developer

Keep the implementation local to the backend service layer and avoid broad changes to the chat route unless necessary for response propagation.

**Implementation status:** Completed. Verified with `python3 -m pytest -q tests/unit/test_llm_client.py tests/integration/test_chat_flow.py` (5 tests passed).
