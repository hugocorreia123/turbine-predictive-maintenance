# Work order draft — engine unit 18
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:56:37 by qwen/qwen3-32b

- Diagnosis: **Fan-section degradation (s_8, s_13 drift) and HPC efficiency loss (s_12 drift)** (confidence 0.92)
- Recommendation: **work_order**
- Action: Replace fan blades and inspect HPC  ·  procedure DOC-2 §2  ·  urgency **high**
- Parts: ['fan blades', 'HPC stator vanes']

## Evidence
- s_12 drift -3.95σ (DOC-2 §2 HPC efficiency loss)
- s_8 drift +3.46σ (DOC-2 §2 fan-section degradation)
- s_13 drift +2.8σ (DOC-2 §2 fan-section degradation)

Citations: DOC-1 §2, DOC-2 §0, DOC-2 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Fan-section degradation (s_8, s_13 drift) and HPC efficiency loss (s_12 drift)",
  "confidence": 0.92,
  "evidence": [
    "s_12 drift -3.95σ (DOC-2 §2 HPC efficiency loss)",
    "s_8 drift +3.46σ (DOC-2 §2 fan-section degradation)",
    "s_13 drift +2.8σ (DOC-2 §2 fan-section degradation)"
  ],
  "work_order": {
    "action": "Replace fan blades and inspect HPC",
    "procedure_ref": "DOC-2 §2",
    "parts": ["fan blades", "HPC stator vanes"],
    "urgency": "high"
  },
  "doc_citations": ["DOC-1 §2", "DOC-2 §0", "DOC-2 §2", "DOC-3 §5"],
  "recommendation": "work_order"
}
```