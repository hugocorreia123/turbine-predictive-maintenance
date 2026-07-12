# Work order draft — engine unit 82
**DRAFT — PENDING ENGINEER REVIEW** · generated 2026-07-12T02:44:07 by qwen/qwen3-32b

- Diagnosis: **High-Pressure Compressor (HPC) efficiency loss (DOC-2 §0) indicated by HPC outlet pressure drop (s_7), fuel flow increase (s_12), and core speed rise (s_9). Fan-section drift (s_13) suggests secondary fan workload effects.** (confidence 0.92)
- Recommendation: **work_order**
- Action: HPC inspection and efficiency verification  ·  procedure PROC-42 §2.1  ·  urgency **high**
- Parts: ['HPC stator vanes', 'HPC blade set']

## Evidence
- s_7 drift -5.18σ (HPC outlet pressure falls with HPC degradation - DOC-1 §1)
- s_12 drift -4.9σ (fuel flow ratio rises with efficiency loss - DOC-1 §1)
- s_9 drift -2.77σ (core speed rises as core compensates for HPC loss - DOC-1 §1)

Citations: DOC-2 §0, DOC-1 §1, DOC-1 §0

## Full narrative
```json
{
  "diagnosis": "High-Pressure Compressor (HPC) efficiency loss (DOC-2 §0) indicated by HPC outlet pressure drop (s_7), fuel flow increase (s_12), and core speed rise (s_9). Fan-section drift (s_13) suggests secondary fan workload effects.",
  "confidence": 0.92,
  "evidence": [
    "s_7 drift -5.18σ (HPC outlet pressure falls with HPC degradation - DOC-1 §1)",
    "s_12 drift -4.9σ (fuel flow ratio rises with efficiency loss - DOC-1 §1)",
    "s_9 drift -2.77σ (core speed rises as core compensates for HPC loss - DOC-1 §1)"
  ],
  "work_order": {
    "action": "HPC inspection and efficiency verification",
    "procedure_ref": "PROC-42 §2.1",
    "parts": ["HPC stator vanes", "HPC blade set"],
    "urgency": "high"
  },
  "doc_citations": ["DOC-2 §0", "DOC-1 §1", "DOC-1 §0"],
  "recommendation": "work_order"
}
```