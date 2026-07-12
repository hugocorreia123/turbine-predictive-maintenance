# Work order draft — engine unit 96
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T03:08:14 by qwen/qwen3-32b

- Diagnosis: **Slight drift in corrected fan speed (s_13) detected, but RUL remains well above alert threshold.** (confidence 0.65)
- Recommendation: **monitor**
- Action: monitor  ·  procedure None  ·  urgency **PLANNED**
- Parts: None

## Evidence
- s_13 drift: +1.01σ (DOC-1 §1 fan-section health indicator)
- RUL p50: 114.2 cycles (>35 threshold)

Citations: DOC-1 §1, DOC-1 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Slight drift in corrected fan speed (s_13) detected, but RUL remains well above alert threshold.",
  "confidence": 0.65,
  "evidence": [
    "s_13 drift: +1.01σ (DOC-1 §1 fan-section health indicator)",
    "RUL p50: 114.2 cycles (>35 threshold)"
  ],
  "work_order": {
    "action": "monitor",
    "procedure_ref": null,
    "parts": null,
    "urgency": "PLANNED"
  },
  "doc_citations": [
    "DOC-1 §1",
    "DOC-1 §2",
    "DOC-3 §5"
  ],
  "recommendation": "monitor"
}
```