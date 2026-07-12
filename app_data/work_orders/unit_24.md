# Work order draft — engine unit 24
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:52:00 by qwen/qwen3-32b

- Diagnosis: **HPC degradation (primary FD001 mode) indicated by s_9/s_14 drift and compensatory core speed increases** (confidence 0.92)
- Recommendation: **work_order**
- Action: Schedule HPC inspection and blade-tip clearance verification  ·  procedure DOC-2 §1  ·  urgency **high**
- Parts: ['HPC blades', 'HPC casing']

## Evidence
- s_9 +19.55σ drift (core speed compensation)
- s_14 +16.5σ drift (core speed compensation)
- s_11 -5.47σ drift (HPC outlet pressure drop)
- s_7 -4.03σ drift (HPC outlet pressure drop)

Citations: DOC-2 §0, DOC-2 §1, DOC-1 §2

## Full narrative
```json
{
  "diagnosis": "HPC degradation (primary FD001 mode) indicated by s_9/s_14 drift and compensatory core speed increases",
  "confidence": 0.92,
  "evidence": [
    "s_9 +19.55σ drift (core speed compensation)",
    "s_14 +16.5σ drift (core speed compensation)",
    "s_11 -5.47σ drift (HPC outlet pressure drop)",
    "s_7 -4.03σ drift (HPC outlet pressure drop)"
  ],
  "work_order": {
    "action": "Schedule HPC inspection and blade-tip clearance verification",
    "procedure_ref": "DOC-2 §1",
    "parts": ["HPC blades", "HPC casing"],
    "urgency": "high"
  },
  "doc_citations": ["DOC-2 §0", "DOC-2 §1", "DOC-1 §2"],
  "recommendation": "work_order"
}
```