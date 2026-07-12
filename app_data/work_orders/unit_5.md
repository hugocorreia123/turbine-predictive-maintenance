# Work order draft — engine unit 5
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T03:03:39 by qwen/qwen3-32b

- Diagnosis: **Fan-section degradation possible due to s_8 drift, but signature incomplete** (confidence 0.65)
- Recommendation: **monitor**
- Action: monitor  ·  procedure DOC-2 §4  ·  urgency **PLANNED**
- Parts: []

## Evidence
- s_12 drift -1.54σ (DOC-2 §2)
- s_21 drift -1.18σ (DOC-2 §2)
- s_8 drift +1.16σ (DOC-2 §2)
- s_20 drift -1.04σ

Citations: DOC-1 §2, DOC-2 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Fan-section degradation possible due to s_8 drift, but signature incomplete",
  "confidence": 0.65,
  "evidence": [
    "s_12 drift -1.54σ (DOC-2 §2)",
    "s_21 drift -1.18σ (DOC-2 §2)",
    "s_8 drift +1.16σ (DOC-2 §2)",
    "s_20 drift -1.04σ"
  ],
  "work_order": {
    "action": "monitor",
    "procedure_ref": "DOC-2 §4",
    "parts": [],
    "urgency": "PLANNED"
  },
  "doc_citations": ["DOC-1 §2", "DOC-2 §2", "DOC-3 §5"],
  "recommendation": "monitor"
}
```