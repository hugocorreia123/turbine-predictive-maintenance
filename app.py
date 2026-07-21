"""Turbine — Predictive Maintenance Intelligence: interactive demo.

Fleet view (assets ranked by risk) -> asset detail (sensor drift +
RUL interval + the AI-drafted work order) -> results (benchmarks,
calibration, the honest copilot evaluation). Reads committed artifacts
from app_data/ and models/ — no training, no data, no API calls.

Run:  uv run streamlit run app.py
"""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Turbine — Predictive Maintenance",
                   layout="wide", page_icon="🌀")

import turbine_theme as th
th.inject()

ALERT_T = 35


@st.cache_data
def load():
    ev = pd.read_parquet("app_data/engine_evidence.parquet")
    fd004 = json.loads(Path("models/fd004_results.json").read_text())
    base = json.loads(Path("models/baseline_fd001.json").read_text())
    tcn = json.loads(Path("models/tcn_fd001.json").read_text())
    qtl = json.loads(
        Path("models/tcn_quantile_fd001.json").read_text())
    op = json.loads(
        Path("models/operating_point_fd001.json").read_text())
    ce = json.loads(Path("models/copilot_eval.json").read_text())
    js = json.loads(Path("models/judge_summary.json").read_text())
    ag = json.loads(Path("models/judge_agreement.json").read_text())
    return ev, fd004, base, tcn, qtl, op, ce, js, ag


ev, fd004, base, tcn, qtl, op, ce, js, ag = load()
DRIFT = [c for c in ev.columns if c.endswith("_drift_sigma")]

import turbine_friendly as tf

if not tf.show_welcome():
    st.stop()

th.hero(
    "Predictive Maintenance Intelligence",
    "Turbine",
    "Deep time-series models predict Remaining Useful Life with "
    "calibrated uncertainty; an agentic engineer diagnoses the fault "
    "and drafts the work order. AI suggests — the engineer decides "
    "and schedules.",
    "NASA C-MAPSS turbofan benchmark · calibrated, not asserted",
)

op_gbm = op["chosen_gbm"]

# ---------------- active engine — one selector drives every panel ----------------
wo_dir = Path("app_data/work_orders")
investigated = {int(p.stem.split("_")[1])
                for p in wo_dir.glob("unit_*.json")}

fleet = ev.copy()
fleet["max_drift"] = fleet[DRIFT].abs().max(axis=1)
fleet["status"] = np.where(
    fleet["gbm_rul"] < 10, "🔴 critical",
    np.where(fleet["gbm_rul"] < ALERT_T, "🟠 alert", "🟢 ok"))
fleet = fleet.sort_values("gbm_rul").reset_index(drop=True)
fleet["risk_rank"] = fleet.index + 1
_fi = fleet.set_index("unit")

opts = fleet["unit"].tolist()
opts = sorted(opts, key=lambda u: (u not in investigated,
                                   _fi.loc[u, "gbm_rul"]))


def fmt_unit(u):
    row = _fi.loc[u]
    tag = " · 📋 work order ready" if u in investigated else ""
    return (f"Engine {u} — {row['status']} · "
            f"~{row['gbm_rul']:.0f} flights left{tag}")


_wo_default = next((i for i, u in enumerate(opts)
                   if u in investigated), 0)
unit = st.selectbox("🎯 Active engine — pick an asset; every panel "
                    "below follows it", opts, index=_wo_default,
                    format_func=fmt_unit,
                    help="Choosing an engine only changes what you see — "
                         "the four cards, the charts and the work-order "
                         "panel all follow it. Engines marked 📋 come "
                         "with a drafted work order to read.")
r = ev[ev["unit"] == unit].iloc[0]
_row = _fi.loc[unit]
_wo_file = wo_dir / f"unit_{unit}.json"
_wo = json.loads(_wo_file.read_text()) if _wo_file.exists() else None


def engine_vitals(r, row, rank, total, wo):
    """The selected engine's vitals — these change with the case above."""
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Remaining life", f"{r['p50']:.0f} cycles")
        st.caption(f"**Means:** about {r['p50']:.0f} flights left before "
                   f"failure — the calibrated best estimate (p50). Status "
                   f"{row['status']} — risk rank #{rank} of {total} in the "
                   "fleet. The calendar doesn't know this; the sensors do.")
    with c2:
        st.metric("80% confidence window",
                  f"{r['p10_conf']:.0f}–{r['p90_conf']:.0f}")
        st.caption(f"**Means:** the failure most likely lands in this "
                   f"range of cycles, with the {r['p50']:.0f}-cycle "
                   "estimate sitting inside it — calibrated on held-out "
                   "engines, so 80% really behaves like 80%.")
    with c3:
        trends = sorted([(d.replace("_drift_sigma", ""), float(r[d]))
                         for d in DRIFT], key=lambda x: -abs(x[1]))
        s_name, s_sig = trends[0]
        word = ("severe" if abs(s_sig) >= 6 else
                "clear" if abs(s_sig) >= 3 else "mild")
        st.metric("Strongest sensor drift", f"{s_sig:+.1f} σ")
        st.caption(f"**Means:** {word}. Sensor {s_name} sits "
                   f"{abs(s_sig):.1f} standard deviations from this "
                   "engine's own healthy baseline — the physical "
                   "evidence behind the prediction.")
    with c4:
        if wo:
            v = wo.get("verdict", {})
            w = v.get("work_order", {}) or {}
            urg = str(w.get("urgency", v.get("recommendation", "?")))
            st.metric("Work order", urg.replace("_", " ").upper())
            st.caption(f"**Means:** drafted at confidence "
                       f"{v.get('confidence', 0):.2f}, waiting for the "
                       "engineer's signature. Never auto-scheduled.")
        else:
            st.metric("Work order", "Pick a 📋 engine")
            st.caption(f"**Means:** the demo ships drafted work orders "
                       f"for {len(investigated)} engines — this isn't "
                       "one. Open the selector and choose any engine "
                       "tagged **📋 work order ready** to read the "
                       "agent's draft.")


engine_vitals(r, _row, int(_row["risk_rank"]), len(fleet), _wo)
st.divider()

tab_fleet, tab_results, tab_method, tab_help = st.tabs(
    ["🔧 Fleet & work orders", "📊 Results", "ℹ️ Method", "❓ Help"])

# ------------------------------------------------------------------
with tab_fleet:
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.subheader("Fleet — ranked by predicted RUL")
        show = fleet[["unit", "status", "gbm_rul", "p10_conf",
                      "p90_conf", "max_drift"]].copy()
        show.columns = ["engine", "status", "predicted life (cycles)",
                        "worst case (p10)", "best case (p90)",
                        "strongest drift (σ)"]
        show["work order"] = show["engine"].apply(
            lambda u: "📋 drafted" if u in investigated else "—")
        st.dataframe(show, hide_index=True, height=340,
                     use_container_width=True)

        # ---- RUL fan + sensor drift ----
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["p10", "p50", "p90"],
            y=[r["p10_conf"], r["p50"], r["p90_conf"]],
            marker_color=["#d62728", "#1f3864", "#2ca02c"],
            text=[f"{r['p10_conf']:.0f}", f"{r['p50']:.0f}",
                  f"{r['p90_conf']:.0f}"], textposition="outside"))
        fig.add_hline(y=ALERT_T, line_dash="dash",
                      annotation_text="alert threshold (35)",
                      line_color="orange")
        fig.update_layout(
            height=260, margin=dict(l=10, r=10, t=30, b=10),
            title=f"Engine {unit}: RUL prediction interval (cycles)",
            yaxis_title="RUL", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        trends = sorted(
            [(d.replace("_drift_sigma", ""), float(r[d]))
             for d in DRIFT], key=lambda x: -abs(x[1]))
        top = [t for t in trends if abs(t[1]) >= 0.5][:8]
        if top:
            fig2 = go.Figure(go.Bar(
                x=[t[1] for t in top], y=[t[0] for t in top],
                orientation="h",
                marker_color=["#d62728" if abs(t[1]) >= 2 else "#ff9896"
                              for t in top]))
            fig2.update_layout(
                height=260, margin=dict(l=10, r=10, t=30, b=10),
                title="Sensor drift vs engine's own baseline (σ)",
                xaxis_title="σ from baseline")
            fig2.add_vline(x=2, line_dash="dot", line_color="grey")
            fig2.add_vline(x=-2, line_dash="dot", line_color="grey")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No sensor exceeds 0.5σ drift — engine reads "
                    "healthy.")

    with right:
        st.subheader("AI work order")
        wo_path = wo_dir / f"unit_{unit}.json"
        if wo_path.exists():
            wo = json.loads(wo_path.read_text())
            v = wo["verdict"]
            st.error(f"**{wo['status']}**", icon="🧑‍🔧")
            a, b, c = st.columns(3)
            a.metric("Diagnosis mode",
                     "HPC" if "hpc" in str(v.get("diagnosis", "")).lower()
                     or "compressor" in str(v.get("diagnosis", "")).lower()
                     else "other")
            b.metric("Confidence", f"{v.get('confidence', 0):.2f}")
            c.metric("Recommendation", str(v.get("recommendation", "?")))
            st.markdown(f"**Diagnosis.** {v.get('diagnosis', '')}")
            if v.get("work_order"):
                w = v["work_order"]
                st.markdown(
                    f"**Work order.** {w.get('action', '')}  \n"
                    f"Procedure {w.get('procedure_ref', '?')} · "
                    f"urgency **{w.get('urgency', '?')}**  \n"
                    f"Parts: {w.get('parts', '—')}")
            if v.get("evidence"):
                st.markdown("**Evidence**")
                for e in v["evidence"]:
                    st.markdown(f"- {e}")
            if v.get("doc_citations"):
                st.caption("Citations: "
                           + ", ".join(v["doc_citations"]))
            st.caption(f"drafted by {wo['model']} · "
                       f"{wo['tool_calling_turns']} tool turns · "
                       f"{wo['generated_at'][:19]}")
            st.warning(
                "Draft only. Measured groundedness is imperfect "
                "(see Results) — an engineer reviews every work "
                "order before scheduling.", icon="⚠️")
        else:
            st.info("No work order drafted for this engine in the demo "
                    "set. Engines with 📋 in the fleet table have one.")

# ------------------------------------------------------------------
with tab_results:
    tf.show_metrics(fd004, qtl, op, ce)
    st.caption("Portfolio-level evaluation — fixed benchmark numbers. "
               "The cards above the tabs follow the selected engine.")
    st.divider()
    a, b = st.columns(2)
    with a:
        st.subheader("RUL accuracy vs published benchmarks")
        df = pd.DataFrame([
            {"benchmark": "FD001 (easy)", "GBM": base["test_rmse"],
             "TCN/ensemble": tcn["test_rmse"]},
            {"benchmark": "FD004 (hard)",
             "GBM": fd004["gbm"]["test_rmse"],
             "TCN/ensemble":
                 fd004["tcn_summary"]["ensemble_test_rmse"]},
        ]).set_index("benchmark")
        st.bar_chart(df, height=280)
        st.caption("Test RMSE, official protocol. **GBM wins the easy "
                   "benchmark; the TCN wins the hard one** — architecture "
                   "pays when the problem is hard enough. Both beat "
                   "published bands (classic ~28–35, deep ~19–24 on "
                   "FD004) thanks to condition normalization + capped "
                   "RUL — not directly comparable to papers with "
                   "different preprocessing.")

        st.subheader("Alerting operating point (FD001)")
        st.markdown(f"""
At the chosen operating point (predicted RUL < {ALERT_T}):
- **{op_gbm['detection']:.0%} detection**, **{op_gbm['false_alarm_rate']:.1%} false alarms**, **{op_gbm['mean_lead_time']:.0f} cycles** mean warning
- Illustrative **€{op['illustrative_net_saving_eur']:,.0f}** per 100 assets vs run-to-failure *(assumptions stated in repo)*
""")
    with b:
        st.subheader("Calibrated uncertainty")
        st.markdown(f"""
Quantile RUL (p10/p50/p90) with **conformal calibration**:
- raw 80% interval covered {qtl['test_coverage_raw']:.0%} (under-covered)
- after conformal correction (±{qtl['conformal_adjustment']:.1f} cycles): **{qtl['test_coverage_conformal']:.0%}** (target 80%)
""")
        st.subheader("Agentic copilot — honest evaluation")
        me = len(ce["mode_errors_on_dying"])
        st.markdown(f"""
| metric | result |
|---|---|
| escalation — dying → work order | **{ce['escalation_dying_correct']}** |
| escalation — healthy not escalated | **{ce['escalation_healthy_correct']}** |
| fault-mode errors on dying engines | **{me}/8** (fan vs HPC) |
| work-order groundedness (judge) | **{js['mean_groundedness']:.3f}** |
| judge vs blind human labels (κ) | **{ag['cohens_kappa']:.3f}** ({ag['raw_agreement']:.0%} raw, n={ag['n']}) |
""")
        st.markdown(
            f"**Honest finding.** The copilot escalates well "
            f"({ce['escalation_dying_correct']} dying caught) but "
            f"misattributes the fault mode {me}/8 times and its "
            f"narratives are frequently imprecise (groundedness "
            f"{js['mean_groundedness']:.2f}). Judge validation gave "
            f"κ={ag['cohens_kappa']:.2f}: human and judge agree on "
            f"clear failures but differ on borderline cases — so the "
            f"judge is strict, not gospel. Either way, the measured "
            f"error rate is the argument for the human-review gate.")

# ------------------------------------------------------------------
with tab_method:
    tf.show_how_it_works()
    st.markdown(f"""
**Pipeline.** NASA C-MAPSS turbofan run-to-failure data → RUL labels
capped at 125 cycles (benchmark convention) → **LightGBM baseline** on
rolled features vs a **temporal CNN** on raw sensor windows (split by
engine, official last-cycle test protocol, RMSE + asymmetric NASA
score) → **quantile head + conformal calibration** for uncertainty →
alerting **operating point** (lead time vs false-alarm rate) → an
**agentic maintenance engineer** (LangGraph ReAct + Groq qwen3-32b)
that reads sensor evidence and a cited maintenance corpus (lexical
RAG) and drafts a work order → **engineer review**.

**Evaluation.** Prognostics: RMSE/NASA on FD001 and FD004 vs published
bands; interval coverage for calibration. Copilot: escalation and
fault-mode accuracy vs ground truth; work-order groundedness by a
**cross-family judge** (gpt-oss-120b auditing qwen3-32b), itself
**validated against blind human labels** (Cohen's κ). Methodology
carried over from [Tracer](https://github.com/hugocorreia123/tracer-aml-graph-intelligence)
and [Voyager](https://github.com/hugocorreia123/voyager).

**Scope & limits.** Single dataset family (C-MAPSS, simulated);
FD001's only fault mode is HPC degradation; the maintenance corpus is
a compiled project reference, not OEM manuals (clearly labeled); RUL
numbers use condition normalization + capping and are not directly
comparable to papers with different preprocessing; the € figure is an
illustrative scaling with stated assumptions.

Code: [github.com/hugocorreia123/turbine-predictive-maintenance](https://github.com/hugocorreia123/turbine-predictive-maintenance)
· Hugo Correia — [LinkedIn](https://www.linkedin.com/in/hugogncorreia)
""")

# ------------------------------------------------------------------
with tab_help:
    tf.show_help(fd004, qtl, op, ce, js, ag)
