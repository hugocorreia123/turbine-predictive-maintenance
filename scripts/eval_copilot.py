"""Turbine — Phase 8a: copilot evaluation batch + objective metrics.

Eval set: 24 engines stratified by TRUE health (which the copilot
never sees): 8 dying (true RUL < 25), 8 mid (25-70), 8 healthy (>90).

Objective metrics (no LLM needed):
  1. ESCALATION correctness — recommendation vs true RUL:
       dying   -> work_order expected
       healthy -> monitor / no_action expected
       mid     -> any of the three accepted (judgment zone), reported
  2. DIAGNOSIS mode accuracy — FD001's only simulated fault mode is
     HPC degradation, so any degrading engine diagnosed as a
     non-HPC mode counts as a mode error.
  3. CITATION validity — every ref in doc_citations must exist in the
     corpus (e.g. 'DOC-2 §0' is invalid). Purely mechanical check.

Resumable: skips units already in work_orders/.
Outputs: runs/eval_set.json, models/copilot_eval.json
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from copilot import investigate, to_md  # noqa: E402

Path("runs").mkdir(exist_ok=True)
Path("work_orders").mkdir(exist_ok=True)

ev = pd.read_parquet("data/processed/engine_evidence.parquet")

# ---------------- valid citation refs from the corpus ----------------
valid_refs = set()
for f in Path("docs_corpus").glob("*.md"):
    text = f.read_text()
    doc_id = text.splitlines()[0].lstrip("# ").split(" — ")[0]
    for m in re.finditer(r"^## (§\d+)", text, re.MULTILINE):
        valid_refs.add(f"{doc_id} {m.group(1)}")
print(f"valid corpus refs: {sorted(valid_refs)}")

# ---------------- eval set ----------------
if Path("runs/eval_set.json").exists():
    eval_set = json.loads(Path("runs/eval_set.json").read_text())
    print(f"reusing eval set ({len(eval_set)} engines)")
else:
    rng = np.random.default_rng(42)
    dying = ev[ev["rul_true"] < 25]["unit"].tolist()
    mid = ev[(ev["rul_true"] >= 25) & (ev["rul_true"] <= 70)]["unit"].tolist()
    healthy = ev[ev["rul_true"] > 90]["unit"].tolist()
    pick = (lambda pool, n: sorted(
        rng.choice(pool, size=min(n, len(pool)), replace=False).tolist()))
    eval_set = ([{"unit": int(u), "band": "dying"} for u in pick(dying, 8)]
                + [{"unit": int(u), "band": "mid"} for u in pick(mid, 8)]
                + [{"unit": int(u), "band": "healthy"}
                   for u in pick(healthy, 8)])
    Path("runs/eval_set.json").write_text(json.dumps(eval_set, indent=2))
    print(f"selected {len(eval_set)} engines "
          f"(8 dying / 8 mid / 8 healthy)")

# ---------------- run (resumable) ----------------
for i, item in enumerate(eval_set):
    u = item["unit"]
    out = Path(f"work_orders/unit_{u}.json")
    if out.exists():
        print(f"[{i+1}/{len(eval_set)}] unit {u}: cached, skip")
        continue
    print(f"[{i+1}/{len(eval_set)}] unit {u} ({item['band']}) ...")
    try:
        wo = investigate(u)
    except Exception as e:
        print(f"  ERROR: {e} (rerun to resume)")
        continue
    out.write_text(json.dumps(wo, indent=2))
    Path(f"work_orders/unit_{u}.md").write_text(to_md(wo))
    v = wo["verdict"]
    print(f"  -> {str(v.get('diagnosis'))[:60]}  "
          f"rec={v.get('recommendation')}")

# ---------------- objective metrics ----------------
rows = []
esc_ok = {"dying": 0, "healthy": 0}
esc_n = {"dying": 0, "healthy": 0}
mid_recs = Counter()
mode_errors = []
bad_citations = []
confidences = []

for item in eval_set:
    u = item["unit"]
    f = Path(f"work_orders/unit_{u}.json")
    if not f.exists():
        continue
    v = json.loads(f.read_text())["verdict"]
    rec = v.get("recommendation")
    diag = str(v.get("diagnosis", "")).lower()
    cits = v.get("doc_citations", []) or []
    confidences.append(v.get("confidence"))
    band = item["band"]
    rows.append({"unit": u, "band": band, "rec": rec,
                 "diagnosis": v.get("diagnosis"),
                 "confidence": v.get("confidence"),
                 "citations": cits})

    if band == "dying":
        esc_n["dying"] += 1
        if rec == "work_order":
            esc_ok["dying"] += 1
    elif band == "healthy":
        esc_n["healthy"] += 1
        if rec in ("monitor", "no_action"):
            esc_ok["healthy"] += 1
    else:
        mid_recs[rec] += 1

    # FD001 fault mode is HPC: a degrading engine diagnosed non-HPC
    if band == "dying" and rec == "work_order" and "hpc" not in diag \
            and "compressor" not in diag:
        mode_errors.append({"unit": u, "diagnosis": v.get("diagnosis")})

    for c in cits:
        if c not in valid_refs:
            bad_citations.append({"unit": u, "ref": c})

metrics = {
    "n_evaluated": len(rows),
    "escalation_dying_correct": f"{esc_ok['dying']}/{esc_n['dying']}",
    "escalation_healthy_correct":
        f"{esc_ok['healthy']}/{esc_n['healthy']}",
    "mid_band_recommendations": dict(mid_recs),
    "mode_errors_on_dying": mode_errors,
    "invalid_citations": bad_citations,
    "confidence_distribution": dict(Counter(confidences)),
    "rows": rows,
}
Path("models/copilot_eval.json").write_text(json.dumps(metrics, indent=2))

print("\n" + "=" * 56)
print("COPILOT OBJECTIVE EVAL")
print("=" * 56)
print(f"escalation — dying flagged work_order:   "
      f"{esc_ok['dying']}/{esc_n['dying']}")
print(f"escalation — healthy NOT escalated:      "
      f"{esc_ok['healthy']}/{esc_n['healthy']}")
print(f"mid band recommendations: {dict(mid_recs)}")
print(f"mode errors on dying engines (non-HPC): {len(mode_errors)}")
for e in mode_errors:
    print(f"   unit {e['unit']}: {e['diagnosis'][:70]}")
print(f"invalid citations: {len(bad_citations)}")
for c in bad_citations:
    print(f"   unit {c['unit']}: '{c['ref']}'")
print(f"confidence values used: "
      f"{sorted(set(c for c in confidences if c is not None))}")
print("\nwrote models/copilot_eval.json")
