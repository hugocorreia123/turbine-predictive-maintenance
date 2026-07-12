# Work order draft — engine unit 83
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T03:07:35 by qwen/qwen3-32b

- Diagnosis: **Engine unit 83 shows no significant sensor drift (all sensors within ±1.0σ of baseline) and predicted RUL (110.4 cycles, p50=124.3) well above alert threshold.** (confidence 0.95)
- Recommendation: **no_action**

## Evidence
- No sensor exceeds 1.0σ drift (get_sensor_trends)

Citations: DOC-2 §3, DOC-2 §4

## Full narrative
```json
{
  "diagnosis": "Engine unit 83 shows no significant sensor drift (all sensors within ±1.0σ of baseline) and predicted RUL (110.4 cycles, p50=124.3) well above alert threshold.",
  "confidence": 0.95,
  "evidence": ["No sensor exceeds 1.0σ drift (get_sensor_trends)"],
  "work_order": null,
  "doc_citations": ["DOC-2 §3", "DOC-2 §4"],
  "recommendation": "no_action"
}
```