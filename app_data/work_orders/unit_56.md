# Work order draft — engine unit 56
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:54:14 by qwen/qwen3-32b

- Diagnosis: **Fan-section degradation (fan blade erosion/FOD, leading-edge wear)** (confidence 0.92)
- Recommendation: **work_order**
- Action: Remove from service at next landing and inspect fan section  ·  procedure DOC-3 §3  ·  urgency **IMMEDIATE**
- Parts: ['fan blades', 'fan leading edges']

## Evidence
- s_8 drift +3.65σ (fan speed, DOC-2 §2)
- s_12 drift -3.54σ (fan speed, DOC-2 §2)
- s_13 drift +2.96σ (fan speed, DOC-2 §2)
- RUL p10=3.8 cycles (<10, DOC-3 §5)

Citations: DOC-1 §2, DOC-2 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Fan-section degradation (fan blade erosion/FOD, leading-edge wear)",
  "confidence": 0.92,
  "evidence": [
    "s_8 drift +3.65σ (fan speed, DOC-2 §2)",
    "s_12 drift -3.54σ (fan speed, DOC-2 §2)",
    "s_13 drift +2.96σ (fan speed, DOC-2 §2)",
    "RUL p10=3.8 cycles (<10, DOC-3 §5)"
  ],
  "work_order": {
    "action": "Remove from service at next landing and inspect fan section",
    "procedure_ref": "DOC-3 §3",
    "parts": ["fan blades", "fan leading edges"],
    "urgency": "IMMEDIATE"
  },
  "doc_citations": ["DOC-1 §2", "DOC-2 §2", "DOC-3 §5"],
  "recommendation": "work_order"
}
```