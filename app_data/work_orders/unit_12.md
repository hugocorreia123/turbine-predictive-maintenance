# Work order draft — engine unit 12
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T03:05:13 by qwen/qwen3-32b

- Diagnosis: **HPC degradation (primary FD001 mode) indicated by sensor drift and slope patterns consistent with compressor efficiency loss** (confidence 0.92)
- Recommendation: **work_order**
- Action: Schedule HPC inspection and performance verification  ·  procedure DOC-2 §1  ·  urgency **monitor**
- Parts: ['HPC blades', 'HPC casing']

## Evidence
- s_14 +3.39σ drift (core speed up)
- s_9 +2.98σ drift (core speed up)
- s_4 +2.19σ drift (LPT temp up)
- s_7 -1.82σ drift (HPC outlet pressure down)
- s_11 +1.57σ drift (HPC outlet pressure down)

Citations: DOC-2 §1, DOC-1 §1, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "HPC degradation (primary FD001 mode) indicated by sensor drift and slope patterns consistent with compressor efficiency loss",
  "confidence": 0.92,
  "evidence": [
    "s_14 +3.39σ drift (core speed up)",
    "s_9 +2.98σ drift (core speed up)",
    "s_4 +2.19σ drift (LPT temp up)",
    "s_7 -1.82σ drift (HPC outlet pressure down)",
    "s_11 +1.57σ drift (HPC outlet pressure down)"
  ],
  "work_order": {
    "action": "Schedule HPC inspection and performance verification",
    "procedure_ref": "DOC-2 §1",
    "parts": ["HPC blades", "HPC casing"],
    "urgency": "monitor"
  },
  "doc_citations": ["DOC-2 §1", "DOC-1 §1", "DOC-3 §5"],
  "recommendation": "work_order"
}
```