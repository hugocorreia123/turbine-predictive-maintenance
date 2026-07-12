"""Turbine — Phase 8c: blind human labeling -> Cohen's kappa.

Presents each of the 24 work orders with its evidence pack and the
corpus sections, and asks you to apply the SAME rubric as the judge:
GROUNDED / PARTIALLY_GROUNDED / UNGROUNDED. The judge's verdict is
hidden until you have labeled everything. Then computes Cohen's kappa
(judge vs you), the validation of the LLM-as-judge.

Resumable: your labels are saved to runs/human_labels.jsonl as you go
(rerun to continue where you left off).

Rubric reminder (same as the judge):
  GROUNDED           - every sensor/value/citation checks out; urgency
                       follows DOC-3 §5.
  PARTIALLY_GROUNDED - minor issues that do NOT change the maintenance
                       decision (e.g. one imprecise citation).
  UNGROUNDED         - factual errors that could mislead the engineer
                       (wrong values, direction errors, a citation that
                       misrepresents the corpus, wrong urgency).

Outputs: runs/human_labels.jsonl, models/judge_agreement.json
"""

import json
import re
from pathlib import Path

import pandas as pd

ev = pd.read_parquet("data/processed/engine_evidence.parquet").set_index(
    "unit")
DRIFT = [c for c in ev.columns if c.endswith("_drift_sigma")]

sections = {}
for f in sorted(Path("docs_corpus").glob("*.md")):
    text = f.read_text()
    doc_id = text.splitlines()[0].lstrip("# ").split(" — ")[0]
    for m in re.split(r"\n(?=## )", text):
        h = re.match(r"## (§\d+)", m)
        if h:
            sections[f"{doc_id} {h.group(1)}"] = m.strip()

LABELS = {"g": "GROUNDED", "p": "PARTIALLY_GROUNDED", "u": "UNGROUNDED"}

eval_set = json.loads(Path("runs/eval_set.json").read_text())
hp = Path("runs/human_labels.jsonl")
done = {}
if hp.exists():
    for line in hp.read_text().splitlines():
        r = json.loads(line)
        done[r["unit"]] = r["human"]


def show(unit):
    r = ev.loc[unit]
    print("\n" + "=" * 66)
    print(f"ENGINE unit {unit}")
    print("=" * 66)
    print(f"cycles observed {int(r['cycles_observed'])} | "
          f"RUL: GBM {r['gbm_rul']:.1f}  p50 {r['p50']:.1f}  "
          f"p10_conf {r['p10_conf']:.1f}  p90_conf {r['p90_conf']:.1f}  "
          f"| alert threshold 35")
    print("\nSENSOR EVIDENCE (drift sigma / slope sigma-per-cycle):")
    trends = sorted(
        [(d.replace("_drift_sigma", ""), float(r[d]),
          float(r[f"{d.replace('_drift_sigma','')}_slope_sigma"]))
         for d in DRIFT], key=lambda x: -abs(x[1]))
    for s, dr, sl in trends:
        if abs(dr) >= 0.5:
            print(f"   {s:<6} drift {dr:+6.2f}   slope {sl:+.3f}")

    wo = json.loads(Path(f"work_orders/unit_{unit}.json").read_text())
    v = wo["verdict"]
    print("\nWORK ORDER:")
    print(f"   diagnosis: {v.get('diagnosis')}")
    print(f"   confidence: {v.get('confidence')}   "
          f"recommendation: {v.get('recommendation')}")
    if v.get("work_order"):
        w = v["work_order"]
        print(f"   action: {w.get('action')} | proc "
              f"{w.get('procedure_ref')} | urgency {w.get('urgency')} "
              f"| parts {w.get('parts')}")
    print(f"   evidence claims:")
    for e in v.get("evidence", []):
        print(f"     - {e}")
    print(f"   citations: {v.get('doc_citations')}")

    refs = [c for c in (v.get("doc_citations") or []) if c in sections]
    if refs:
        print("\nCITED CORPUS SECTIONS (verify claims against these):")
        for rf in dict.fromkeys(refs):
            print(f"   --- {rf} ---")
            for ln in sections[rf].splitlines()[1:6]:
                print(f"     {ln}")


print(f"Blind labeling: {len(eval_set)} work orders. "
      f"Already done: {len(done)}.")
print("For each: type g / p / u  (or s to skip, q to quit).")
print("The judge's verdicts stay hidden until every item is labeled.\n")

with hp.open("a") as fout:
    for item in eval_set:
        u = item["unit"]
        if u in done:
            continue
        show(u)
        while True:
            ans = input("\n  your label [g/p/u, s, q]: ").strip().lower()
            if ans == "q":
                print("saved so far; rerun to continue.")
                raise SystemExit
            if ans == "s":
                break
            if ans in LABELS:
                fout.write(json.dumps(
                    {"unit": u, "human": LABELS[ans]}) + "\n")
                fout.flush()
                done[u] = LABELS[ans]
                break
            print("  enter g, p, u, s, or q.")

# ---------------- kappa once complete ----------------
judge = {json.loads(l)["unit"]: json.loads(l)["verdict"]
         for l in Path("runs/judgments.jsonl").read_text().splitlines()}
pairs = [(done[u], judge[u]) for u in done
         if u in judge and judge[u] in LABELS.values()]

if len(pairs) < len(eval_set):
    print(f"\nlabeled {len(done)}/{len(eval_set)}; "
          f"finish all to compute kappa.")
    raise SystemExit

cats = ["GROUNDED", "PARTIALLY_GROUNDED", "UNGROUNDED"]
idx = {c: i for i, c in enumerate(cats)}
n = len(pairs)
po = sum(1 for a, b in pairs if a == b) / n
# expected agreement from marginals
from collections import Counter
ha = Counter(a for a, _ in pairs)
ja = Counter(b for _, b in pairs)
pe = sum((ha[c] / n) * (ja[c] / n) for c in cats)
kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0

# 3x3 confusion (rows human, cols judge)
conf = [[0] * 3 for _ in range(3)]
for a, b in pairs:
    conf[idx[a]][idx[b]] += 1

agreement = {"n": n, "raw_agreement": round(po, 3),
             "cohens_kappa": round(kappa, 3),
             "human_dist": dict(ha), "judge_dist": dict(ja),
             "confusion_rows_human_cols_judge": conf,
             "categories": cats}
Path("models/judge_agreement.json").write_text(
    json.dumps(agreement, indent=2))

print("\n" + "=" * 56)
print("JUDGE VALIDATION — human vs gpt-oss-120b")
print("=" * 56)
print(f"n = {n}   raw agreement {po:.1%}   Cohen's kappa {kappa:.3f}")
print(f"confusion (rows=human, cols=judge) order {cats}:")
for i, c in enumerate(cats):
    print(f"  {c:<20} {conf[i]}")
print("wrote models/judge_agreement.json")
