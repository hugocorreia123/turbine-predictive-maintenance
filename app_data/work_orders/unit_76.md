# Work order draft — engine unit 76
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:55:14 by qwen/qwen3-32b

- Diagnosis: **High-Pressure Compressor (HPC) efficiency loss (DOC-2 §0)** (confidence 0.92)
- Recommendation: **work_order**
- Action: Schedule HPC inspection and efficiency testing  ·  procedure PROC-45 §2.1  ·  urgency **critical (RUL < 20 cycles)**
- Parts: ['HPC stator vanes', 'HPC blade assembly']

## Evidence
- s_9 drift +10.7σ (DOC-1 §2)
- s_14 drift +10.5σ (DOC-1 §2)
- s_12 drift -7.6σ (DOC-1 §2)
- RUL p50=8.7 cycles (<35 threshold)

Citations: DOC-1 §0, DOC-2 §0, DOC-1 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "High-Pressure Compressor (HPC) efficiency loss (DOC-2 §0)",
  "confidence": 0.92,
  "evidence": [
    "s_9 drift +10.7σ (DOC-1 §2)",
    "s_14 drift +10.5σ (DOC-1 §2)",
    "s_12 drift -7.6σ (DOC-1 §2)",
    "RUL p50=8.7 cycles (<35 threshold)"
  ],
  "work_order": {
    "action": "Schedule HPC inspection and efficiency testing",
    "procedure_ref": "PROC-45 §2.1",
    "parts": ["HPC stator vanes", "HPC blade assembly"],
    "urgency": "critical (RUL < 20 cycles)"
  },
  "doc_citations": ["DOC-1 §0", "DOC-2 §0", "DOC-1 §2", "DOC-3 §5"],
  "recommendation": "work_order"
}
```