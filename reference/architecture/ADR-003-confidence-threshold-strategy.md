# ADR-003: Confidence Threshold Strategy for Escalation Availability

**Status:** Proposed
**Date:** 2026-04-23
**Deciders:** Architect, Tech Lead

## Context

FEATURE-007 adds a confidence-based escalation trigger: the escalation button appears in the chat UI only when the AI's response confidence is below a threshold. This prevents escalation fatigue for users with high-confidence responses.

Current system:
- Chat endpoint calculates confidence score (0.0-1.0) based on RAG source relevance
- escalation_available flag is sent to frontend
- Frontend shows button only when escalation_available=true

Key question: What confidence threshold value (0.0-1.0) indicates an unresolved query? Too high threshold = too many escalations (noise). Too low threshold = users stuck with bad answers (friction).

From BA Critical Hypothesis H-05: "Escalation threshold <30% correctly identifies unresolved queries. Escalation accuracy >= 90%"

**Triggering ASR:**
- MODERATE: Confidence Threshold Calibration (FEATURE-007)
- Quality Attribute: User Experience (Escalation availability matches true unresolved queries)

## Decision Drivers

- **User Experience**: Escalation button should appear when user truly needs help, not for every slightly uncertain response.
- **Support Load**: Too low threshold = excessive escalations, overwhelming admin team. Too high threshold = users frustrated by unresolved queries.
- **Data Validation**: Hypothesis H-05 suggests threshold <30% targets 90% accuracy. Must measure this empirically.
- **Configurability**: Threshold should be tunable without code deployment (allows A/B testing, adjustment).
- **Feedback Loop**: Escalation rate and resolution rate should inform threshold adjustments.

## Considered Options

### Option 1: Fixed Threshold (0.3)

Hardcoded threshold: escalation_available = true IFF confidence < 0.3

```python
escalation_available = response_confidence < 0.3
```

- Pro: Simple, no configuration needed
- Pro: Based on BA hypothesis (H-05 suggests <30%)
- Pro: Easy to test and validate
- Con: Not tunable without code deployment
- Con: Threshold may be wrong for different query types
- Con: No A/B testing capability
- Con: Cannot adapt as user behavior changes

### Option 2: Dynamic Threshold (Configuration)

Threshold stored in database or config file. Can be adjusted at runtime without deployment.

```python
threshold = settings.ESCALATION_CONFIDENCE_THRESHOLD  # 0.3
escalation_available = response_confidence < threshold
```

- Pro: Tunable without deployment (ops can adjust)
- Pro: Enables A/B testing (different companies test different thresholds)
- Pro: Can adapt based on observed escalation rates
- Con: Adds operational complexity (someone must monitor and adjust)
- Con: Multiple threshold values mean multiple code paths (harder to test)
- Con: Requires monitoring/alerting to know when threshold is "wrong"

### Option 3: ML-Based Dynamic Threshold

Confidence threshold learned from user feedback. If user escalates a high-confidence response, model learns to lower threshold.

```
Track: response_confidence, user_escalated?, admin_response_quality
Periodically recompute optimal threshold via ML
```

- Pro: Adapts automatically to user behavior
- Pro: Maximizes "right" escalations (minimizes false positives/negatives)
- Con: High complexity (needs ML pipeline, training, etc.)
- Con: Requires significant user feedback data (cold start problem)
- Con: Harder to debug (non-transparent decision-making)
- Con: Overkill for MVP (premature optimization)

## Decision

**Proposed Option:** Option 2 (Dynamic Threshold with Configuration)

**Rationale:**

MVP needs a sensible starting point (0.3 from BA hypothesis H-05) plus the ability to observe and adjust. Option 2 provides both.

Starting with 0.3 based on H-05 is reasonable, but we must measure empirically:
- Escalation rate per week
- What % of escalations actually needed admin help (resolution rate)
- Did escalated queries have false negatives (users without escalation button who needed help)?

Once deployed, ops team can adjust threshold based on metrics:
- If escalation rate too high: increase threshold (e.g., 0.35)
- If escalation rate too low: decrease threshold (e.g., 0.25)

Rationale for rejecting Option 1: Fixed threshold removes feedback loop. If threshold is wrong, we cannot fix it without redeployment.

Rationale for rejecting Option 3: ML-based approach is premature for MVP. Start with human-tuned threshold, only escalate to ML if pattern becomes clear.

**Implementation approach:**
1. Add ESCALATION_CONFIDENCE_THRESHOLD to settings with default 0.3
2. In chat endpoint: `escalation_available = response_confidence < settings.ESCALATION_CONFIDENCE_THRESHOLD`
3. Add monitoring dashboard tracking escalation_rate, resolution_rate, avg_confidence_of_escalated_responses
4. Document in ops runbook how to tune threshold based on metrics

## Consequences

### Positive
- Starts with theoretically justified threshold (0.3 from H-05)
- Tunable at runtime (no deployment needed)
- Easy to measure impact of threshold changes
- Enables A/B testing if needed
- Ops team can respond to excessive escalation rates

### Negative
- Requires monitoring and active tuning (operational overhead)
- Multiple threshold values could theoretically diverge (if different settings)
- No automatic adaptation (human must adjust)
- Early deployment may have "wrong" threshold (high noise or false negatives)

### Risks
- **Risk: Threshold is too high, escalations overwhelm admin team** - Mitigation: Monitor escalation_rate daily, alert if >threshold, ops increases threshold
- **Risk: Threshold is too low, users frustrated by lack of escalation button** - Mitigation: Monitor user escalation_attempts (button clicks), if high relative to escalations, lower threshold
- **Risk: Confidence calculation itself is wrong** - Mitigation: Validate confidence_score correlation with actual answer quality (e.g., compare with user ratings if available)

## Implementation Notes

- Add to settings/config.py:
  ```python
  ESCALATION_CONFIDENCE_THRESHOLD = float(os.getenv("ESCALATION_CONFIDENCE_THRESHOLD", "0.3"))
  ```
- In chat endpoint (app/api/routes/chat.py):
  ```python
  response = generate_chat_response(query, context)
  escalation_available = response.confidence < settings.ESCALATION_CONFIDENCE_THRESHOLD
  return {"message": response.text, "confidence": response.confidence, "escalation_available": escalation_available}
  ```
- Add monitoring metrics (Prometheus, CloudWatch, etc.):
  - escalations_created_per_day
  - escalations_resolved_per_day
  - avg_confidence_of_escalated_responses
  - avg_confidence_of_non_escalated_responses
- Ops runbook entry:
  ```
  To tune escalation threshold:
  1. Check metrics dashboard (escalations/day, resolution_rate)
  2. If escalations/day > [threshold], increase ESCALATION_CONFIDENCE_THRESHOLD (e.g., 0.3 -> 0.35)
  3. Monitor for 3 days
  4. If escalations/day still high, increase further
  ```

## Related Decisions

- FEATURE-007: Confidence-Based Escalation Flag (implements this ADR)
- Future: ADR on confidence score calculation improvements (if needed after MVP)

## References

- Confidence Thresholding in ML: https://en.wikipedia.org/wiki/Confidence_interval
- RAG Evaluation: https://docs.llamaindex.ai/en/stable/module_guides/evaluating/
