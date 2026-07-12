# Work order draft — engine unit 30
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T03:06:22 by qwen/qwen3-32b

- Diagnosis: **HPC degradation (DOC-2 §1) indicated by s_9 (+1.6σ), s_14 (+1.82σ), s_12 (+1.14σ drift), and s_4 (+1.28σ) consistent with compressor efficiency loss** (confidence 0.75)
- Recommendation: **monitor**
- Action: monitor  ·  procedure DOC-2 §1  ·  urgency **low**
- Parts: []

## Evidence
- s_9 drift +1.6σ (core speed compensating ↑)
- s_14 drift +1.82σ (core speed ↑)
- s_12 drift +1.14σ (fuel flow ratio ↑)
- s_4 drift +1.28σ (LPT temp ↑)
- s_11 drift -1.31σ (HPC outlet pressure ↓)

Citations: DOC-2 §1, DOC-1 §1

## Full narrative
```json
{
  "diagnosis": "HPC degradation (DOC-2 §1) indicated by s_9 (+1.6σ), s_14 (+1.82σ), s_12 (+1.14σ drift), and s_4 (+1.28σ) consistent with compressor efficiency loss",
  "confidence": 0.75,
  "evidence": [
    "s_9 drift +1.6σ (core speed compensating ↑)",
    "s_14 drift +1.82σ (core speed ↑)",
    "s_12 drift +1.14σ (fuel flow ratio ↑)",
    "s_4 drift +1.28σ (LPT temp ↑)",
    "s_11 drift -1.31σ (HPC outlet pressure ↓)"
  ],
  "work_order": {
    "action": "monitor",
    "procedure_ref": "DOC-2 §1",
    "parts": [],
    "urgency": "low"
  },
  "doc_citations": ["DOC-2 §1", "DOC-1 §1"],
  "recommendation": "monitor"
}
```