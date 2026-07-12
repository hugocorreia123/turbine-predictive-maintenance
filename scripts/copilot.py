"""Turbine — Phase 7b: agentic maintenance engineer.

A ReAct agent (LangGraph + Groq qwen3-32b — same stack whose ReAct
topology was validated in Voyager) investigates one engine at a time:

  tools:
    get_asset_summary  — cycles observed, RUL predictions (GBM point,
                         quantile p10/p50/p90 conformal), alert status
    get_sensor_trends  — per-sensor drift vs own baseline (sigma) and
                         recent slope; raw evidence, no interpretation
    search_docs        — lexical (TF-IDF) retrieval over the project's
                         sectioned maintenance corpus; returns doc/§ ids
                         the agent MUST cite

  output: fenced JSON — diagnosis, confidence, evidence, work_order
          {action, procedure_ref, parts, urgency}, doc_citations,
          recommendation (work_order | monitor | no_action)
  Every draft is stamped DRAFT — PENDING ENGINEER REVIEW.

The agent NEVER sees true RUL. Ground truth stays in the eval.

Usage:
  uv run python scripts/copilot.py --unit 100     # dying engine
  uv run python scripts/copilot.py --unit 47      # healthy engine
  uv run python scripts/copilot.py --top 5        # riskiest engines

Outputs: work_orders/unit_{u}.json + .md
"""

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
assert os.environ.get("GROQ_API_KEY"), "GROQ_API_KEY missing (.env)"

MODEL = "qwen/qwen3-32b"
ALERT_T = 35   # Phase 4 chosen operating point
SENSOR_COLS = None  # filled at load

ev = pd.read_parquet("data/processed/engine_evidence.parquet").set_index(
    "unit")
DRIFT = [c for c in ev.columns if c.endswith("_drift_sigma")]
SLOPE = [c for c in ev.columns if c.endswith("_slope_sigma")]

# ---------------- corpus: sectioned + TF-IDF ----------------
sections = []
for f in sorted(Path("docs_corpus").glob("*.md")):
    text = f.read_text()
    doc_title = text.splitlines()[0].lstrip("# ").strip()
    doc_id = doc_title.split(" — ")[0]  # e.g. DOC-2
    for m in re.split(r"\n(?=## )", text):
        sec_m = re.match(r"## (§\d+[^\n]*)", m)
        if not sec_m:
            continue  # skip unlabeled preamble blocks
        sec_id = sec_m.group(1).split(" ")[0]
        sections.append({"ref": f"{doc_id} {sec_id}",
                         "title": (sec_m.group(1) if sec_m else doc_title),
                         "text": m.strip()})
_vec = TfidfVectorizer(stop_words="english")
_mat = _vec.fit_transform([s["text"] for s in sections])

CURRENT_UNIT = None


@tool
def get_asset_summary() -> str:
    """Summary of the engine under investigation: cycles observed so
    far, RUL predictions (GBM point estimate; quantile p10/p50/p90
    with conformal bounds), and whether it breaches the fleet alert
    threshold (predicted RUL < 35 cycles)."""
    r = ev.loc[CURRENT_UNIT]
    return json.dumps({
        "unit": int(CURRENT_UNIT),
        "cycles_observed": int(r["cycles_observed"]),
        "rul_point_gbm": round(float(r["gbm_rul"]), 1),
        "rul_p50": round(float(r["p50"]), 1),
        "rul_p10_conformal": round(float(r["p10_conf"]), 1),
        "rul_p90_conformal": round(float(r["p90_conf"]), 1),
        "alert_threshold": ALERT_T,
        "alert": bool(r["gbm_rul"] < ALERT_T),
    })


@tool
def get_sensor_trends(min_abs_sigma: float = 1.0) -> str:
    """Per-sensor evidence for this engine: drift of the recent window
    vs the engine's own early-life baseline (in baseline standard
    deviations) and the recent per-cycle slope (also in sigmas). Only
    sensors with |drift| >= min_abs_sigma are returned, largest first.
    Raw evidence — no interpretation."""
    r = ev.loc[CURRENT_UNIT]
    out = []
    for d in DRIFT:
        s = d.replace("_drift_sigma", "")
        drift = float(r[d])
        if abs(drift) >= min_abs_sigma:
            out.append({"sensor": s, "drift_sigma": drift,
                        "slope_sigma_per_cycle":
                            float(r[f"{s}_slope_sigma"])})
    out.sort(key=lambda x: -abs(x["drift_sigma"]))
    return json.dumps(out if out else
                      [{"note": f"no sensor exceeds "
                                f"{min_abs_sigma} sigma drift"}])


@tool
def search_docs(query: str) -> str:
    """Search the maintenance reference corpus (sensor map,
    failure-mode signatures, procedures & urgency policy). Returns the
    top matching sections with their citation refs (e.g. 'DOC-2 §1').
    Cite these refs in the work order."""
    qv = _vec.transform([query])
    sims = cosine_similarity(qv, _mat)[0]
    top = np.argsort(-sims)[:3]
    return json.dumps([{"ref": sections[i]["ref"],
                        "text": sections[i]["text"][:900]}
                       for i in top if sims[i] > 0.05])


SYSTEM = """You are a turbofan maintenance engineer copilot. You are
given ONE engine flagged by the fleet's predictive-maintenance system.
Investigate with your tools and produce a work-order draft.

Rules:
- Use get_asset_summary and get_sensor_trends first; consult
  search_docs to match the sensor signature to a failure mode and to
  choose the procedure and urgency. Base EVERY claim on tool output;
  cite corpus sections by ref (e.g. "DOC-2 §1") for every doc-based
  statement. Never invent sensors, numbers, or citations.
- Not every engine needs work. If trends are weak or absent
  (DOC-2 §3/§4), say so: recommendation "monitor" or "no_action".
- Urgency must follow DOC-3 §5 exactly, using the RUL predictions.
- End with EXACTLY one JSON block fenced as ```json ... ``` with keys:
  diagnosis (string), confidence (0-1),
  evidence (list of short strings citing sensors/values),
  work_order {action, procedure_ref, parts, urgency} or null,
  doc_citations (list of refs used),
  recommendation ("work_order" | "monitor" | "no_action").
"""

llm = ChatGroq(model=MODEL, temperature=0.0, max_retries=8,
               reasoning_format="hidden")
agent = create_react_agent(
    llm, [get_asset_summary, get_sensor_trends, search_docs])


def investigate(unit: int) -> dict:
    global CURRENT_UNIT
    CURRENT_UNIT = unit
    task = (f"{SYSTEM}\n\nInvestigate engine unit {unit}. "
            f"Start with get_asset_summary.")
    result = agent.invoke({"messages": [("user", task)]},
                          config={"recursion_limit": 40})
    final = result["messages"][-1].content
    m = re.search(r"```json\s*(\{.*?\})\s*```", final, re.DOTALL)
    verdict = json.loads(m.group(1)) if m else {"parse_error": final[-400:]}
    n_tools = sum(1 for msg in result["messages"]
                  if getattr(msg, "tool_calls", None))
    return {"unit": unit,
            "status": "DRAFT — PENDING ENGINEER REVIEW",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "tool_calling_turns": n_tools,
            "verdict": verdict,
            "narrative": final}


def to_md(wo: dict) -> str:
    v = wo["verdict"]
    lines = [f"# Work order draft — engine unit {wo['unit']}",
             f"**{wo['status']}** · generated {wo['generated_at'][:19]} "
             f"by {wo['model']}",
             "",
             f"- Diagnosis: **{v.get('diagnosis', '?')}** "
             f"(confidence {v.get('confidence', '?')})",
             f"- Recommendation: **{v.get('recommendation', '?')}**"]
    if v.get("work_order"):
        w = v["work_order"]
        lines += [f"- Action: {w.get('action')}  ·  procedure "
                  f"{w.get('procedure_ref')}  ·  urgency "
                  f"**{w.get('urgency')}**",
                  f"- Parts: {w.get('parts')}"]
    lines += ["", "## Evidence"]
    lines += [f"- {e}" for e in v.get("evidence", [])]
    lines += ["", f"Citations: {', '.join(v.get('doc_citations', []))}",
              "", "## Full narrative", wo["narrative"]]
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", type=int, default=None)
    ap.add_argument("--top", type=int, default=0,
                    help="investigate the N riskiest engines")
    args = ap.parse_args()

    Path("work_orders").mkdir(exist_ok=True)
    if args.unit is not None:
        targets = [args.unit]
    else:
        ranked = ev.sort_values("gbm_rul").index.tolist()
        targets = [int(u) for u in ranked[: args.top or 5]]

    print(f"investigating engines: {targets}")
    for u in targets:
        wo = investigate(u)
        Path(f"work_orders/unit_{u}.json").write_text(
            json.dumps(wo, indent=2))
        Path(f"work_orders/unit_{u}.md").write_text(to_md(wo))
        v = wo["verdict"]
        print(f"  unit {u}: {v.get('diagnosis')}  "
              f"conf={v.get('confidence')}  "
              f"rec={v.get('recommendation')}  "
              f"({wo['tool_calling_turns']} tool turns)")
    print("wrote work_orders/unit_*.json + .md")
