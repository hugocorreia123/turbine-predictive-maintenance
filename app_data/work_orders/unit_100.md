# Work order draft — engine unit 100
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:41:51 by qwen/qwen3-32b

- Diagnosis: **High-Pressure Compressor (HPC) degradation (DOC-2 §1) with significant sensor drift in s_9 (core speed) and s_14 (fuel flow ratio), consistent with blade-tip clearance growth and erosion.** (confidence 0.92)
- Recommendation: **work_order**
- Action: Borescope inspection of HPC stages 1–3  ·  procedure DOC-3 §1  ·  urgency **high**
- Parts: []

## Evidence
- s_9 drift +22.29σ (core speed compensation)
- s_14 drift +19.27σ (fuel flow ratio)
- s_11 drift +4.55σ (HPC outlet pressure)
- s_4 drift +4.35σ (LPT inlet temperature)

Citations: DOC-2 §1, DOC-3 §1, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "High-Pressure Compressor (HPC) degradation (DOC-2 §1) with significant sensor drift in s_9 (core speed) and s_14 (fuel flow ratio), consistent with blade-tip clearance growth and erosion.",
  "confidence": 0.92,
  "evidence": [
    "s_9 drift +22.29σ (core speed compensation)",
    "s_14 drift +19.27σ (fuel flow ratio)",
    "s_11 drift +4.55σ (HPC outlet pressure)",
    "s_4 drift +4.35σ (LPT inlet temperature)"
  ],
  "work_order": {
    "action": "Borescope inspection of HPC stages 1–3",
    "procedure_ref": "DOC-3 §1",
    "parts": [],
    "urgency": "high"
  },
  "doc_citations": ["DOC-2 §1", "DOC-3 §1", "DOC-3 §5"],
  "recommendation": "work_order"
}
```