# Work order draft — engine unit 94
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T03:03:09 by qwen/qwen3-32b

- Diagnosis: **Sensor s_7 shows significant negative drift (-2.56σ) and worsening slope (-0.054σ/cycle), consistent with DOC-1 §0 (T25 temperature sensor degradation). Other sensors show mixed trends but below 2σ threshold.** (confidence 0.75)
- Recommendation: **work_order**
- Action: Schedule inspection  ·  procedure DOC-3 §1  ·  urgency **PLANNED**
- Parts: ['T25 temperature sensor (s_7)', 'related thermocouple wiring']

## Evidence
- s_7 drift -2.56σ (DOC-1 §2 significant degradation threshold)
- s_7 slope -0.054σ/cycle (worsening trend)
- RUL p10=41.4 cycles (>35 threshold, DOC-3 §5)

Citations: DOC-1 §0, DOC-1 §2, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Sensor s_7 shows significant negative drift (-2.56σ) and worsening slope (-0.054σ/cycle), consistent with DOC-1 §0 (T25 temperature sensor degradation). Other sensors show mixed trends but below 2σ threshold.",
  "confidence": 0.75,
  "evidence": [
    "s_7 drift -2.56σ (DOC-1 §2 significant degradation threshold)",
    "s_7 slope -0.054σ/cycle (worsening trend)",
    "RUL p10=41.4 cycles (>35 threshold, DOC-3 §5)"
  ],
  "work_order": {
    "action": "Schedule inspection",
    "procedure_ref": "DOC-3 §1",
    "parts": ["T25 temperature sensor (s_7)", "related thermocouple wiring"],
    "urgency": "PLANNED"
  },
  "doc_citations": ["DOC-1 §0", "DOC-1 §2", "DOC-3 §5"],
  "recommendation": "work_order"
}
```