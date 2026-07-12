# Work order draft — engine unit 34
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:43:24 by qwen/qwen3-32b

- Diagnosis: **HPC degradation (primary FD001 mode) indicated by s_7, s_11, s_12, s_14 drift consistent with DOC-2 §1 signature** (confidence 0.92)
- Recommendation: **work_order**
- Action: Schedule HPC inspection and blade-tip clearance adjustment  ·  procedure DOC-3 §2.1.4  ·  urgency **immediate**
- Parts: ['HPC blades', 'HPC seals']

## Evidence
- s_11 drift -8.26σ (HPC outlet pressure down)
- s_12 drift +7.39σ (fuel flow ratio up)
- s_14 drift +7.33σ (core speed compensation)
- s_7 drift -7.0σ (HPC outlet pressure down)
- RUL p50 4.5 cycles (<35 threshold)

Citations: DOC-2 §1, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "HPC degradation (primary FD001 mode) indicated by s_7, s_11, s_12, s_14 drift consistent with DOC-2 §1 signature",
  "confidence": 0.92,
  "evidence": [
    "s_11 drift -8.26σ (HPC outlet pressure down)",
    "s_12 drift +7.39σ (fuel flow ratio up)",
    "s_14 drift +7.33σ (core speed compensation)",
    "s_7 drift -7.0σ (HPC outlet pressure down)",
    "RUL p50 4.5 cycles (<35 threshold)"
  ],
  "work_order": {
    "action": "Schedule HPC inspection and blade-tip clearance adjustment",
    "procedure_ref": "DOC-3 §2.1.4",
    "parts": ["HPC blades", "HPC seals"],
    "urgency": "immediate"
  },
  "doc_citations": ["DOC-2 §1", "DOC-3 §5"],
  "recommendation": "work_order"
}
```