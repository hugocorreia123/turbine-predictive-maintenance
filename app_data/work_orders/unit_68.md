# Work order draft — engine unit 68
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:45:04 by qwen/qwen3-32b

- Diagnosis: **High-Pressure Compressor (HPC) degradation (primary FD001 mode)** (confidence 0.92)
- Recommendation: **work_order**
- Action: Replace HPC blades and seals  ·  procedure DOC-2 §1  ·  urgency **critical**
- Parts: ['HPC blades', 'HPC seals']

## Evidence
- s_11 (HPC outlet pressure) drift -4.77σ, slope -0.11σ/cycle
- s_9 (core speed) drift +6.23σ, slope +0.116σ/cycle
- s_3 (HPC outlet temp) drift +5.04σ, slope +0.123σ/cycle
- s_4 (LPT outlet temp) drift +5.56σ, slope +0.081σ/cycle

Citations: DOC-1 §1, DOC-2 §0, DOC-2 §1, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "High-Pressure Compressor (HPC) degradation (primary FD001 mode)",
  "confidence": 0.92,
  "evidence": [
    "s_11 (HPC outlet pressure) drift -4.77σ, slope -0.11σ/cycle",
    "s_9 (core speed) drift +6.23σ, slope +0.116σ/cycle",
    "s_3 (HPC outlet temp) drift +5.04σ, slope +0.123σ/cycle",
    "s_4 (LPT outlet temp) drift +5.56σ, slope +0.081σ/cycle"
  ],
  "work_order": {
    "action": "Replace HPC blades and seals",
    "procedure_ref": "DOC-2 §1",
    "parts": ["HPC blades", "HPC seals"],
    "urgency": "critical"
  },
  "doc_citations": ["DOC-1 §1", "DOC-2 §0", "DOC-2 §1", "DOC-3 §5"],
  "recommendation": "work_order"
}
```