# Work order draft — engine unit 42
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:47:12 by qwen/qwen3-32b

- Diagnosis: **High-Pressure Compressor (HPC) efficiency loss with cascading gas-path degradation** (confidence 0.92)
- Recommendation: **work_order**
- Action: Replace HPC assembly and inspect gas-path components  ·  procedure DOC-4 §7.2  ·  urgency **critical**
- Parts: ['HPC rotor/stator kit', 'LPT nozzles']

## Evidence
- s_3 drift +2.87σ (HPC outlet temp ↑ per DOC-1 §1)
- s_7 drift -5.42σ (HPC outlet pressure ↓ per DOC-1 §1)
- s_11 drift -4.88σ (HPC outlet static pressure ↓ per DOC-1 §1)
- s_4 drift +4.38σ (LPT outlet temp ↑ per DOC-1 §1)

Citations: DOC-1 §1, DOC-2 §0, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "High-Pressure Compressor (HPC) efficiency loss with cascading gas-path degradation",
  "confidence": 0.92,
  "evidence": [
    "s_3 drift +2.87σ (HPC outlet temp ↑ per DOC-1 §1)",
    "s_7 drift -5.42σ (HPC outlet pressure ↓ per DOC-1 §1)",
    "s_11 drift -4.88σ (HPC outlet static pressure ↓ per DOC-1 §1)",
    "s_4 drift +4.38σ (LPT outlet temp ↑ per DOC-1 §1)"
  ],
  "work_order": {
    "action": "Replace HPC assembly and inspect gas-path components",
    "procedure_ref": "DOC-4 §7.2",
    "parts": ["HPC rotor/stator kit", "LPT nozzles"],
    "urgency": "critical"
  },
  "doc_citations": ["DOC-1 §1", "DOC-2 §0", "DOC-3 §5"],
  "recommendation": "work_order"
}
```