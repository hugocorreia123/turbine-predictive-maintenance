# Work order draft — engine unit 92
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:55:46 by qwen/qwen3-32b

- Diagnosis: **Engine unit 92 shows significant drift in multiple sensors (s_12: -3.91σ, s_7: -3.36σ, s_20: -3.26σ) with a predicted RUL of 20.3 cycles (p10 bound 14.9 cycles), breaching the alert threshold.** (confidence 0.92)
- Recommendation: **work_order**
- Action: Schedule inspection and component replacement  ·  procedure DOC-3 §3  ·  urgency **URGENT**
- Parts: ['High-pressure compressor blades', 'Turbine inlet temperature sensors']

## Evidence
- s_12 drift -3.91σ (DOC-1 §2)
- s_7 drift -3.36σ (DOC-1 §2)
- RUL p10=14.9 < 35 (alert threshold) (DOC-3 §5)

Citations: DOC-1 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Engine unit 92 shows significant drift in multiple sensors (s_12: -3.91σ, s_7: -3.36σ, s_20: -3.26σ) with a predicted RUL of 20.3 cycles (p10 bound 14.9 cycles), breaching the alert threshold.",
  "confidence": 0.92,
  "evidence": [
    "s_12 drift -3.91σ (DOC-1 §2)",
    "s_7 drift -3.36σ (DOC-1 §2)",
    "RUL p10=14.9 < 35 (alert threshold) (DOC-3 §5)"
  ],
  "work_order": {
    "action": "Schedule inspection and component replacement",
    "procedure_ref": "DOC-3 §3",
    "parts": ["High-pressure compressor blades", "Turbine inlet temperature sensors"],
    "urgency": "URGENT"
  },
  "doc_citations": ["DOC-1 §2", "DOC-3 §5"],
  "recommendation": "work_order"
}
```