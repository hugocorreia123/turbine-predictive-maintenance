# Work order draft — engine unit 72
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T03:02:07 by qwen/qwen3-32b

- Diagnosis: **HPC degradation (DOC-2 §1) with mixed sensor evidence** (confidence 0.7)
- Recommendation: **monitor**
- Action: monitor  ·  procedure DOC-2 §3  ·  urgency **low**
- Parts: []

## Evidence
- s_11 drift +3.06σ (HPC outlet pressure)
- s_12 drift -2.16σ (fuel flow ratio)
- s_4 drift +1.86σ (LPT temperature)
- s_7 drift -1.71σ (HPC outlet pressure)

Citations: DOC-2 §1, DOC-2 §3

## Full narrative
```json
{
  "diagnosis": "HPC degradation (DOC-2 §1) with mixed sensor evidence",
  "confidence": 0.7,
  "evidence": [
    "s_11 drift +3.06σ (HPC outlet pressure)",
    "s_12 drift -2.16σ (fuel flow ratio)",
    "s_4 drift +1.86σ (LPT temperature)",
    "s_7 drift -1.71σ (HPC outlet pressure)"
  ],
  "work_order": {
    "action": "monitor",
    "procedure_ref": "DOC-2 §3",
    "parts": [],
    "urgency": "low"
  },
  "doc_citations": ["DOC-2 §1", "DOC-2 §3"],
  "recommendation": "monitor"
}
```