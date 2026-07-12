# Work order draft — engine unit 49
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:53:13 by qwen/qwen3-32b

- Diagnosis: **Fan-section degradation (s_8, s_13 drift) with secondary HPC efficiency loss (s_11, s_12 decline). RUL < 35 cycles.** (confidence 0.92)
- Recommendation: **work_order**
- Action: Fan-section inspection and HPC efficiency assessment  ·  procedure DOC-2 §2  ·  urgency **critical**
- Parts: ['fan blades', 'HPC stator vanes']

## Evidence
- s_8 drift +8.45σ (fan speed drift ↑) [DOC-1 §1]
- s_13 drift +6.48σ (corrected fan speed ↑) [DOC-1 §1]
- s_11 drift -6.96σ (HPC outlet pressure ↓) [DOC-1 §1]
- s_12 drift -5.97σ (fuel flow ratio ↑) [DOC-1 §1]

Citations: DOC-1 §1, DOC-2 §0, DOC-2 §2

## Full narrative
```json
{
  "diagnosis": "Fan-section degradation (s_8, s_13 drift) with secondary HPC efficiency loss (s_11, s_12 decline). RUL < 35 cycles.",
  "confidence": 0.92,
  "evidence": [
    "s_8 drift +8.45σ (fan speed drift ↑) [DOC-1 §1]",
    "s_13 drift +6.48σ (corrected fan speed ↑) [DOC-1 §1]",
    "s_11 drift -6.96σ (HPC outlet pressure ↓) [DOC-1 §1]",
    "s_12 drift -5.97σ (fuel flow ratio ↑) [DOC-1 §1]"
  ],
  "work_order": {
    "action": "Fan-section inspection and HPC efficiency assessment",
    "procedure_ref": "DOC-2 §2",
    "parts": ["fan blades", "HPC stator vanes"],
    "urgency": "critical"
  },
  "doc_citations": ["DOC-1 §1", "DOC-2 §0", "DOC-2 §2"],
  "recommendation": "work_order"
}
```