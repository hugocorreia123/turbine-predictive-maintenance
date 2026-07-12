# Work order draft — engine unit 58
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T03:01:03 by qwen/qwen3-32b

- Diagnosis: **HPC degradation (DOC-2 §1 signature: s_4↑, s_7↓, s_11↑/s_12↓ conflicting with baseline signature)** (confidence 0.75)
- Recommendation: **work_order**
- Action: Schedule HPC inspection and blade-tip clearance check  ·  procedure DOC-3 §3  ·  urgency **URGENT**
- Parts: ['HPC blades', 'HPC seals']

## Evidence
- s_11 drift +3.69σ (↑), slope +0.059σ/cycle
- s_4 drift +3.48σ (↑), slope +0.051σ/cycle
- s_7 drift -3.29σ (↓), slope -0.047σ/cycle
- s_8 drift +3.07σ (↑), slope +0.063σ/cycle

Citations: DOC-1 §2, DOC-2 §1, DOC-3 §3, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "HPC degradation (DOC-2 §1 signature: s_4↑, s_7↓, s_11↑/s_12↓ conflicting with baseline signature)",
  "confidence": 0.75,
  "evidence": [
    "s_11 drift +3.69σ (↑), slope +0.059σ/cycle",
    "s_4 drift +3.48σ (↑), slope +0.051σ/cycle",
    "s_7 drift -3.29σ (↓), slope -0.047σ/cycle",
    "s_8 drift +3.07σ (↑), slope +0.063σ/cycle"
  ],
  "work_order": {
    "action": "Schedule HPC inspection and blade-tip clearance check",
    "procedure_ref": "DOC-3 §3",
    "parts": ["HPC blades", "HPC seals"],
    "urgency": "URGENT"
  },
  "doc_citations": ["DOC-1 §2", "DOC-2 §1", "DOC-3 §3", "DOC-3 §5"],
  "recommendation": "work_order"
}
```