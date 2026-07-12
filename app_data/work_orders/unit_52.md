# Work order draft — engine unit 52
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T03:00:15 by qwen/qwen3-32b

- Diagnosis: **HPC degradation (DOC-2 §1) indicated by s_9 (+10.3σ), s_14 (+15.4σ), and s_11 (-4.3σ) drift consistent with blade-tip clearance growth and compressor inefficiency** (confidence 0.92)
- Recommendation: **work_order**
- Action: Schedule HPC inspection and blade-tip clearance measurement  ·  procedure DOC-2 §1  ·  urgency **URGENT**
- Parts: ['HPC blades', 'compressor casing']

## Evidence
- s_14 drift +15.39σ (p10 RUL=33.6 cycles)
- s_9 drift +10.3σ
- s_11 drift -4.29σ
- s_7 drift -3.39σ
- s_4 drift +3.94σ

Citations: DOC-1 §2, DOC-2 §1, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "HPC degradation (DOC-2 §1) indicated by s_9 (+10.3σ), s_14 (+15.4σ), and s_11 (-4.3σ) drift consistent with blade-tip clearance growth and compressor inefficiency",
  "confidence": 0.92,
  "evidence": [
    "s_14 drift +15.39σ (p10 RUL=33.6 cycles)",
    "s_9 drift +10.3σ",
    "s_11 drift -4.29σ",
    "s_7 drift -3.39σ",
    "s_4 drift +3.94σ"
  ],
  "work_order": {
    "action": "Schedule HPC inspection and blade-tip clearance measurement",
    "procedure_ref": "DOC-2 §1",
    "parts": ["HPC blades", "compressor casing"],
    "urgency": "URGENT"
  },
  "doc_citations": ["DOC-1 §2", "DOC-2 §1", "DOC-3 §5"],
  "recommendation": "work_order"
}
```