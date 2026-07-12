# Work order draft — engine unit 81
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:46:15 by qwen/qwen3-32b

- Diagnosis: **Fan-section degradation (DOC-2 §2) with multiple sensors indicating fan speed (s_8, s_13), bypass ratio (s_15), and core parameter shifts. RUL predictions indicate imminent failure (p10 RUL=1.1 cycles).** (confidence 0.95)
- Recommendation: **work_order**
- Action: remove from service for fan-section inspection and blade replacement  ·  procedure DOC-3 §3  ·  urgency **IMMEDIATE**
- Parts: ['fan blades', 'fan speed sensors']

## Evidence
- s_11 drift +7.5σ (fan inlet temp)
- s_7 drift -6.45σ (compressor discharge pressure)
- s_8 drift +5.81σ (fan speed)
- p10 RUL=1.1 cycles (DOC-3 §5)

Citations: DOC-1 §2, DOC-2 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Fan-section degradation (DOC-2 §2) with multiple sensors indicating fan speed (s_8, s_13), bypass ratio (s_15), and core parameter shifts. RUL predictions indicate imminent failure (p10 RUL=1.1 cycles).",
  "confidence": 0.95,
  "evidence": [
    "s_11 drift +7.5σ (fan inlet temp)", 
    "s_7 drift -6.45σ (compressor discharge pressure)",
    "s_8 drift +5.81σ (fan speed)",
    "p10 RUL=1.1 cycles (DOC-3 §5)"
  ],
  "work_order": {
    "action": "remove from service for fan-section inspection and blade replacement",
    "procedure_ref": "DOC-3 §3",
    "parts": ["fan blades", "fan speed sensors"],
    "urgency": "IMMEDIATE"
  },
  "doc_citations": ["DOC-1 §2", "DOC-2 §2", "DOC-3 §5"],
  "recommendation": "work_order"
}
```