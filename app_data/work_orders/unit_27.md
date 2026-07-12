# Work order draft — engine unit 27
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:57:47 by qwen/qwen3-32b

- Diagnosis: **Potential HPC degradation with mixed sensor trends** (confidence 0.6)
- Recommendation: **monitor**
- Action: monitor  ·  procedure DOC-3 §4  ·  urgency **low**
- Parts: []

## Evidence
- s_7 drift -2.09σ (HPC outlet pressure ↓, DOC-1 §1)
- s_12 drift -2.17σ (fuel flow ratio ↓, contrary to DOC-2 §1)
- s_11 drift +2.09σ (HPC outlet pressure ↑, opposite DOC-2 §1)
- s_4 drift +1.87σ (LPT outlet temp ↑, end-of-life indicator DOC-1 §1)

Citations: DOC-1 §1, DOC-2 §1, DOC-2 §0, DOC-3 §5

## Full narrative
```json
{
  "diagnosis": "Potential HPC degradation with mixed sensor trends",
  "confidence": 0.6,
  "evidence": [
    "s_7 drift -2.09σ (HPC outlet pressure ↓, DOC-1 §1)",
    "s_12 drift -2.17σ (fuel flow ratio ↓, contrary to DOC-2 §1)",
    "s_11 drift +2.09σ (HPC outlet pressure ↑, opposite DOC-2 §1)",
    "s_4 drift +1.87σ (LPT outlet temp ↑, end-of-life indicator DOC-1 §1)"
  ],
  "work_order": {
    "action": "monitor",
    "procedure_ref": "DOC-3 §4",
    "parts": [],
    "urgency": "low"
  },
  "doc_citations": ["DOC-1 §1", "DOC-2 §1", "DOC-2 §0", "DOC-3 §5"],
  "recommendation": "monitor"
}
```