"""Turbine — Phase 8b: cross-family LLM judge for work orders.

gpt-oss-120b (different family from the qwen3-32b copilot — no
self-preference) audits each of the 24 eval work orders against a
FIXED evidence pack. No tools; the judge sees exactly:

  1. the engine's evidence row (per-sensor drift/slope sigmas, RUL
     predictions; true RUL withheld)
  2. the FULL TEXT of every corpus section the copilot cited
     (plus DOC-2 and DOC-3 §5 always, for mode/urgency checks)
  3. the copilot's verdict JSON + narrative

Rubric (both must hold for GROUNDED):
  A. NUMERIC GROUNDEDNESS — every sensor named exists in the
     evidence; every σ/value quoted matches within ±0.15σ; RUL
     numbers match predictions; urgency follows DOC-3 §5 given
     the stated RULs.
  B. CITATION FAITHFULNESS — each citation's section actually
     supports the claim attached to it (content, not just existence;
     §0 refs count as imprecise-citation issues).

Verdict: GROUNDED (1.0) / PARTIALLY_GROUNDED (0.5) / UNGROUNDED (0.0)
plus a typed issues list.

Resumable via runs/judgments.jsonl.
Outputs: runs/judgments.jsonl, models/judge_summary.json
"""

import json
import os
import re
import time
from collections import Counter
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
JUDGE_MODEL = "openai/gpt-oss-120b"

ev = pd.read_parquet("data/processed/engine_evidence.parquet").set_index(
    "unit")
DRIFT = [c for c in ev.columns if c.endswith("_drift_sigma")]

# ---------------- corpus sections by ref ----------------
sections = {}
for f in sorted(Path("docs_corpus").glob("*.md")):
    text = f.read_text()
    doc_id = text.splitlines()[0].lstrip("# ").split(" — ")[0]
    for m in re.split(r"\n(?=## )", text):
        h = re.match(r"## (§\d+)", m)
        if h:
            sections[f"{doc_id} {h.group(1)}"] = m.strip()

ALWAYS = ["DOC-2 §1", "DOC-2 §2", "DOC-2 §3", "DOC-2 §4", "DOC-3 §5"]


def evidence_pack(unit: int) -> str:
    r = ev.loc[unit]
    sens = []
    for d in DRIFT:
        s = d.replace("_drift_sigma", "")
        sens.append(f"{s}: drift {r[d]:+.2f} sigma, "
                    f"slope {r[f'{s}_slope_sigma']:+.3f} sigma/cycle")
    return (f"unit {unit} | cycles observed {int(r['cycles_observed'])}\n"
            f"RUL predictions: GBM point {r['gbm_rul']:.1f} | "
            f"p50 {r['p50']:.1f} | p10_conf {r['p10_conf']:.1f} | "
            f"p90_conf {r['p90_conf']:.1f} | alert threshold 35\n"
            f"sensor evidence (drift = late window vs own early "
            f"baseline):\n  " + "\n  ".join(sens))


RUBRIC = """You are auditing an AI-drafted turbofan maintenance work
order against fixed evidence. You have: (1) the engine's sensor
evidence and RUL predictions, (2) the full text of relevant corpus
sections, (3) the AI's work order (verdict JSON + narrative).

Check:
A. NUMERIC GROUNDEDNESS - every sensor the work order names must
   exist in the evidence; every sigma/value quoted must match the
   evidence within +/-0.15 sigma; RUL numbers must match the given
   predictions; the urgency must follow DOC-3 §5 given the RULs it
   states.
B. CITATION FAITHFULNESS - for each citation, the cited section must
   actually support the specific claim it is attached to. A citation
   to a nonexistent or preamble section ('§0') is an
   'imprecise_citation' issue. A section that exists but does not say
   what is claimed is a 'misattributed_citation' issue.

Also flag: sensors misnamed relative to DOC-1 (e.g. calling s_14
'fuel flow ratio' when DOC-1 defines it as corrected core speed),
invented numbers, direction errors (claiming a rise where evidence
shows a fall).

Respond ONLY with JSON:
{"verdict": "GROUNDED" | "PARTIALLY_GROUNDED" | "UNGROUNDED",
 "issues": [{"type": "wrong_value|invented_sensor|direction_error|
             sensor_misnamed|imprecise_citation|misattributed_citation|
             urgency_policy_violation|other",
             "detail": "<one line>"}],
 "notes": "<one sentence>"}
GROUNDED = no issues. PARTIALLY_GROUNDED = minor issues that do not
change the maintenance decision. UNGROUNDED = factual errors that
could mislead the engineer."""

llm = ChatGroq(model=JUDGE_MODEL, temperature=0.0, max_retries=8)

out_path = Path("runs/judgments.jsonl")
done = set()
if out_path.exists():
    for line in out_path.read_text().splitlines():
        done.add(json.loads(line)["unit"])

eval_set = json.loads(Path("runs/eval_set.json").read_text())
results = []
with out_path.open("a") as fout:
    for i, item in enumerate(eval_set):
        u = item["unit"]
        if u in done:
            print(f"[{i+1}/{len(eval_set)}] unit {u}: judged, skip")
            continue
        wo = json.loads(Path(f"work_orders/unit_{u}.json").read_text())
        cits = (wo["verdict"].get("doc_citations") or [])
        refs = list(dict.fromkeys(
            [c for c in cits if c in sections] + ALWAYS))
        corpus_txt = "\n\n".join(f"[{r}]\n{sections[r]}" for r in refs)
        prompt = (f"{RUBRIC}\n\n=== EVIDENCE ===\n{evidence_pack(u)}\n\n"
                  f"=== CORPUS SECTIONS ===\n{corpus_txt}\n\n"
                  f"=== WORK ORDER (verdict JSON) ===\n"
                  f"{json.dumps(wo['verdict'], indent=1)}\n\n"
                  f"=== WORK ORDER (narrative) ===\n"
                  f"{wo['narrative'][:3500]}")
        print(f"[{i+1}/{len(eval_set)}] judging unit {u} "
              f"({item['band']}) ...")
        raw = llm.invoke(prompt).content
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        try:
            j = json.loads(m.group(0))
        except Exception:
            j = {"verdict": "PARSE_ERROR", "issues": [],
                 "notes": raw[-200:]}
        rec = {"unit": u, "band": item["band"], **j}
        fout.write(json.dumps(rec) + "\n")
        fout.flush()
        print(f"   -> {j.get('verdict')}  "
              f"({len(j.get('issues', []))} issues)")
        time.sleep(1)

# ---------------- summary ----------------
rows = [json.loads(line)
        for line in out_path.read_text().splitlines()]
score_map = {"GROUNDED": 1.0, "PARTIALLY_GROUNDED": 0.5,
             "UNGROUNDED": 0.0}
scored = [r for r in rows if r["verdict"] in score_map]
mean = sum(score_map[r["verdict"]] for r in scored) / max(len(scored), 1)
verdicts = Counter(r["verdict"] for r in rows)
issue_types = Counter(i["type"] for r in rows
                      for i in r.get("issues", []))

summary = {"n": len(rows), "verdicts": dict(verdicts),
           "mean_groundedness": round(mean, 3),
           "issue_taxonomy": dict(issue_types)}
Path("models/judge_summary.json").write_text(
    json.dumps(summary, indent=2))

print("\n" + "=" * 56)
print(f"JUDGE SUMMARY ({JUDGE_MODEL})")
print("=" * 56)
print(f"verdicts: {dict(verdicts)}")
print(f"mean groundedness: {mean:.3f}")
print("issue taxonomy:")
for t, n in issue_types.most_common():
    print(f"  {t:<26} {n}")
print("wrote runs/judgments.jsonl, models/judge_summary.json")
