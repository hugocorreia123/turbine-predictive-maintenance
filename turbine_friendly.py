"""Turbine — friendly UI layer.

Welcome tour, plain-language metric explanations, honesty box, and a help
tab. Streamlit only — no other dependencies. Same pattern as Mandate's
friendly UI, in Turbine's voice: written for the maintenance planner.
"""

import streamlit as st

_TOUR_KEY = "turbine_tour_done"


# ------------------------------------------------------------------ welcome
def show_welcome() -> bool:
    """One-time plain-language tour. Returns True once dismissed."""
    if st.session_state.get(_TOUR_KEY):
        return True

    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:
        st.title("🌀 Turbine")
        st.subheader("Your calendar says the part is fine. The sensors disagree.")
        st.markdown(
            """
Maintenance by calendar replaces parts that are still healthy and misses
the ones that are quietly dying. Turbine reads the **sensors** instead:
deep time-series models estimate how many flight cycles each engine has
left — **with calibrated uncertainty**, so "about 30 cycles" comes with
an honest confidence band — and an AI copilot drafts the work order for
the engineer to approve.

**What you can do here**

- **🔧 Fleet & work orders** — the fleet ranked by risk. Open a critical
  engine, see its sensor drift, its remaining-life interval, and the
  drafted work order.
- **📊 Results** — every claim measured: two benchmarks, calibration,
  the alerting trade-off, and an honest copilot evaluation (including
  the parts that failed).
- **ℹ️ Method** — how it works, in plain language first.

**What this will not do**

It never schedules anything on its own. The AI drafts; **the engineer
decides and signs**. That is a design rule, and the evaluation shows why:
the copilot reasons well but narrates imprecisely.

*Data: NASA C-MAPSS turbofan benchmark (simulated run-to-failure). No
real fleet data.*
"""
        )
        c1, c2 = st.columns(2)
        if c1.button("Start exploring", type="primary", use_container_width=True):
            st.session_state[_TOUR_KEY] = True
            st.rerun()
        if c2.button("Skip the intro", use_container_width=True):
            st.session_state[_TOUR_KEY] = True
            st.rerun()
    return False


def show_replay() -> None:
    """Small control to replay the intro tour."""
    if st.button("↻ Replay the intro", help="Show the welcome tour again"):
        st.session_state[_TOUR_KEY] = False
        st.rerun()


# ------------------------------------------------------------------ metrics
def show_metrics(fd004, qtl, op, ce) -> None:
    """Headline metrics with a plain-language 'means' line under each.

    Takes the live loaded artifacts — values are computed, never hardcoded.
    """
    op_gbm = op["chosen_gbm"]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "RUL error — hard benchmark (FD004)",
            f"{fd004['tcn_summary']['ensemble_test_rmse']:.2f} RMSE",
            f"beats GBM {fd004['gbm']['test_rmse']:.2f}",
        )
        st.caption(
            "**Means:** on the hard benchmark, remaining-life predictions are "
            f"off by about {fd004['tcn_summary']['ensemble_test_rmse']:.0f} "
            "flight cycles on average — and the deep model beats the "
            "classical one on every seed."
        )
    with c2:
        st.metric(
            "Uncertainty calibration",
            f"{qtl['test_coverage_conformal']:.0%}",
            "conformal 80% interval",
        )
        st.caption(
            "**Means:** when the model gives an 80%-confidence window for a "
            f"failure, the true value lands inside it {qtl['test_coverage_conformal']:.0%} "
            "of the time — measured, not assumed."
        )
    with c3:
        st.metric(
            "Failure warning @ low false alarms",
            f"{op_gbm['mean_lead_time']:.0f} cycles",
            f"{op_gbm['false_alarm_rate']:.1%} false alarms",
        )
        st.caption(
            f"**Means:** you get about {op_gbm['mean_lead_time']:.0f} cycles "
            "of warning before a failure, and only "
            f"{op_gbm['false_alarm_rate']:.1%} of alerts waste your time."
        )
    with c4:
        st.metric(
            "Copilot escalation (dying engines)",
            f"{ce['escalation_dying_correct']}",
            "flagged for work order",
        )
        st.caption(
            "**Means:** every dying engine in the evaluation was correctly "
            "flagged for a work order — but the engineer still signs it, "
            "because the copilot's narratives are not fully reliable "
            "(see Results)."
        )


# ------------------------------------------------------------------ method
def show_how_it_works() -> None:
    """Plain-language pipeline story for the top of the Method tab."""
    st.markdown(
        """
#### How it works, in one breath

Each engine streams 21 sensor readings per flight cycle. A temporal
convolutional network reads the raw sensor windows and predicts
**how many cycles of life remain** — as an interval (p10 / p50 / p90),
conformally calibrated so the band means what it says. A threshold sweep
turns predictions into **alerts** with a measured lead-time /
false-alarm trade-off. For each alerted engine, an agentic copilot reads
the sensor drift, diagnoses the likely fault, and **drafts a work
order** — which a human engineer reviews, corrects, and signs.

**Does this affect what you see?** Only if you care why the numbers are
trustworthy: on the easy benchmark the classical model actually *wins*
(kept, not hidden), the deep model earns its keep on the hard one, and
the copilot's work orders were audited by a cross-family judge that was
itself checked against blind human labels.
"""
    )
    st.markdown("---")


# ------------------------------------------------------------------ help
def show_help(fd004=None, qtl=None, op=None, ce=None, js=None, ag=None) -> None:
    """Help tab: orientation, mini-glossary, and the honesty box."""
    st.header("❓ Help")

    st.markdown(
        """
#### What am I looking at?

A predictive-maintenance demo on the NASA C-MAPSS turbofan benchmark.
Simulated engines run to failure; Turbine predicts each engine's
remaining life, raises alerts, and drafts work orders for human sign-off.

**Start here:** open **🔧 Fleet & work orders**, click a 🔴 critical
engine, and read its drafted work order next to the sensor evidence.

#### Words on the screen, in plain language

- **RUL** — Remaining Useful Life: how many flight cycles are left
  before failure.
- **RMSE** — average prediction error, in cycles. Lower is better.
- **Conformal interval** — a confidence band that was *calibrated on
  held-out engines*, so "80%" really behaves like 80%.
- **Lead time** — how many cycles before the failure the alert fires.
- **False alarm** — an alert on an engine that was actually fine.
- **Drift (σ)** — how far a sensor has moved from its healthy baseline,
  in standard deviations.
- **Cross-family judge** — the model that graded the copilot's work
  orders is from a different family than the copilot, and the judge was
  itself validated against blind human labels (Cohen's κ).
"""
    )

    st.markdown("#### The honesty box")
    kappa_line = ""
    if ag:
        kappa_line = (
            f"- **The judge itself has limits.** Blind human labels vs the "
            f"LLM judge: Cohen's κ = {ag.get('kappa', 0):.3f} "
            f"(n = {ag.get('n', '?')}). Human and judge agree on clearly "
            "broken outputs but split on borderline ones — so LLM-as-judge "
            "is trusted here for catching clear failures, not for grading "
            "nuance.\n"
        )
    ce_line = ""
    if ce:
        ce_line = (
            f"- **The copilot narrates imprecisely.** It escalated all "
            f"{ce.get('escalation_dying_correct', '?')} dying engines, but "
            "its written narratives contain factual slips (fault-mode and "
            "citation errors) — the measured reason the human gate exists.\n"
        )
    st.markdown(
        f"""
- **On the easy benchmark, the classical model wins.** A tuned GBM beats
  the deep model on FD001; the deep model earns its complexity only on
  the hard FD004. Both results are kept.
- **Raw uncertainty under-covered.** The 80% intervals covered only 62%
  before conformal calibration; the calibration step is what makes the
  band honest.
{ce_line}{kappa_line}- **Simulated data.** C-MAPSS is a simulation benchmark — the pattern
  transfers, the exact numbers do not. The € impact figure is an
  illustrative scaling with stated assumptions.
- **AI suggests — the engineer decides and schedules.** Always.
"""
    )

    st.markdown(
        """
#### Links

[GitHub repository](https://github.com/hugocorreia123/turbine-predictive-maintenance)
· Hugo Correia — [LinkedIn](https://www.linkedin.com/in/hugogncorreia)
"""
    )
    show_replay()
