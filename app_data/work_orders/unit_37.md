# Work order draft — engine unit 37
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:52:14 by qwen/qwen3-32b

- Diagnosis: **Engine 37 shows significant sensor drift in s_14 (-5.06σ), s_13 (4.14σ), and s_8 (3.44σ), with RUL prediction (p50: 24.4 cycles) below the 35-cycle alert threshold.** (confidence 0.92)
- Recommendation: **work_order**
- Action: Schedule §3 inspection and monitor s_14/s_13 degradation  ·  procedure DOC-3 §5  ·  urgency **URGENT**
- Parts: []

## Evidence
- s_14 drift -5.06σ (DOC-1 §2)
- s_13 drift 4.14σ (DOC-1 §2)
- RUL p50 24.4 < 35 (DOC-3 §5)

Citations: DOC-1 §0, DOC-1 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Engine 37 shows significant sensor drift in s_14 (-5.06σ), s_13 (4.14σ), and s_8 (3.44σ), with RUL prediction (p50: 24.4 cycles) below the 35-cycle alert threshold.",
  "confidence": 0.92,
  "evidence": [
    "s_14 drift -5.06σ (DOC-1 §2)",
    "s_13 drift 4.14σ (DOC-1 §2)",
    "RUL p50 24.4 < 35 (DOC-3 §5)"
  ],
  "work_order": {
    "action": "Schedule §3 inspection and monitor s_14/s_13 degradation",
    "procedure_ref": "DOC-3 §5",
    "parts": [],
    "urgency": "URGENT"
  },
  "doc_citations": ["DOC-1 §0", "DOC-1 §2", "DOC-3 §5"],
  "recommendation": "work_order"
}
```