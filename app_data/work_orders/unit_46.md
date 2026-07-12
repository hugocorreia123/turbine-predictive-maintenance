# Work order draft — engine unit 46
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:59:28 by qwen/qwen3-32b

- Diagnosis: **Fan-section degradation (DOC-2 §2) indicated by s_8, s_13, and s_15 drift** (confidence 0.85)
- Recommendation: **work_order**
- Action: schedule_inspection  ·  procedure DOC-2 §2  ·  urgency **PLANNED**
- Parts: ['fan blades', 'bypass duct']

## Evidence
- s_9 drift 5.13σ (DOC-1 §2)
- s_14 drift 3.95σ (DOC-1 §2)
- s_11 drift 3.18σ (DOC-1 §2)
- s_15 drift 2.31σ (DOC-2 §2)
- s_13 drift 1.33σ (DOC-2 §2)
- s_8 drift 1.41σ (DOC-2 §2)

Citations: DOC-1 §2, DOC-2 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Fan-section degradation (DOC-2 §2) indicated by s_8, s_13, and s_15 drift",
  "confidence": 0.85,
  "evidence": [
    "s_9 drift 5.13σ (DOC-1 §2)",
    "s_14 drift 3.95σ (DOC-1 §2)",
    "s_11 drift 3.18σ (DOC-1 §2)",
    "s_15 drift 2.31σ (DOC-2 §2)",
    "s_13 drift 1.33σ (DOC-2 §2)",
    "s_8 drift 1.41σ (DOC-2 §2)"
  ],
  "work_order": {
    "action": "schedule_inspection",
    "procedure_ref": "DOC-2 §2",
    "parts": ["fan blades", "bypass duct"],
    "urgency": "PLANNED"
  },
  "doc_citations": ["DOC-1 §2", "DOC-2 §2", "DOC-3 §5"],
  "recommendation": "work_order"
}
```