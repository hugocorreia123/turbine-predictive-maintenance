# Work order draft — engine unit 43
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:58:22 by qwen/qwen3-32b

- Diagnosis: **High-Pressure Compressor (HPC) efficiency loss (DOC-2 §0)** (confidence 0.75)
- Recommendation: **work_order**
- Action: Schedule inspection  ·  procedure DOC-3 §5.2  ·  urgency **medium**
- Parts: ['HPC stator blades', 'Compressor vanes']

## Evidence
- s_11 drift +2.28σ (T25), slope +0.043σ/cycle
- s_7 drift -2.05σ (P30), slope -0.028σ/cycle
- s_8 drift +2.01σ (P15), slope +0.016σ/cycle

Citations: DOC-2 §0, DOC-1 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "High-Pressure Compressor (HPC) efficiency loss (DOC-2 §0)",
  "confidence": 0.75,
  "evidence": [
    "s_11 drift +2.28σ (T25), slope +0.043σ/cycle",
    "s_7 drift -2.05σ (P30), slope -0.028σ/cycle",
    "s_8 drift +2.01σ (P15), slope +0.016σ/cycle"
  ],
  "work_order": {
    "action": "Schedule inspection",
    "procedure_ref": "DOC-3 §5.2",
    "parts": ["HPC stator blades", "Compressor vanes"],
    "urgency": "medium"
  },
  "doc_citations": ["DOC-2 §0", "DOC-1 §2", "DOC-3 §5"],
  "recommendation": "work_order"
}
```