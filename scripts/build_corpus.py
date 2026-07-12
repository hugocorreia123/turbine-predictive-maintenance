"""Turbine — Phase 7a: docs corpus + per-engine evidence.

1. Writes docs_corpus/*.md — a small, curated turbofan maintenance
   reference (sensor map, failure-mode signatures, maintenance
   procedures). Compiled reference content based on the public
   C-MAPSS documentation ("Damage Propagation Modeling", Saxena et
   al. 2008) and standard turbomachinery FMEA practice; written for
   this project and clearly labeled as such. The copilot must cite
   sections from THESE docs — citation faithfulness is auditable.

2. Builds data/processed/engine_evidence.parquet — per FD001-test-
   engine sensor-trend evidence: per-sensor drift (late-window mean
   vs early-window baseline, in baseline std units) and slope, plus
   observed cycles. This is what the copilot's tools serve.

Run:  uv run python scripts/build_corpus.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/CMaps")
CORPUS = Path("docs_corpus")
CORPUS.mkdir(exist_ok=True)
OUT = Path("data/processed")

COLS = (["unit", "cycle", "setting_1", "setting_2", "setting_3"]
        + [f"s_{i}" for i in range(1, 22)])
DROP = ["s_1", "s_5", "s_6", "s_10", "s_16", "s_18", "s_19"]
SENSORS = [f"s_{i}" for i in range(1, 22) if f"s_{i}" not in DROP]

# ------------------------------------------------------------------
# 1. corpus
# ------------------------------------------------------------------
(CORPUS / "sensor_map.md").write_text("""# DOC-1 — C-MAPSS Turbofan Sensor Map
*Compiled project reference, based on the public C-MAPSS dataset
documentation (Saxena et al., 2008, "Damage Propagation Modeling for
Aircraft Engine Run-to-Failure Simulation").*

## §1 Station sensors
- **s_2** — LPC outlet temperature (°R). Rises with compressor-section degradation.
- **s_3** — HPC outlet temperature (°R). Primary indicator of High-Pressure Compressor health; sustained upward drift signals HPC efficiency loss.
- **s_4** — LPT outlet temperature (°R). Rises as overall gas-path efficiency degrades; strong end-of-life indicator.
- **s_7** — HPC outlet pressure (psia). FALLS as HPC degrades (loss of pressure rise capability).
- **s_8** — Physical fan speed (rpm). Drifts with fan-section degradation.
- **s_9** — Physical core speed (rpm). Rises as the core works harder to hold thrust with a degraded HPC.
- **s_11** — HPC outlet static pressure (psia). Falls with HPC degradation.
- **s_12** — Fuel flow ratio to Ps30 (pps/psi). Rises: more fuel needed per unit pressure as efficiency drops.
- **s_13** — Corrected fan speed (rpm). Fan-section health indicator.
- **s_14** — Corrected core speed (rpm). Rises with core degradation.
- **s_15** — Bypass ratio. Shifts as fan/core balance changes with degradation.
- **s_17** — Bleed enthalpy. Rises with degradation.
- **s_20** — High-pressure turbine coolant bleed (lbm/s). Falls with degradation.
- **s_21** — Low-pressure turbine coolant bleed (lbm/s). Falls with degradation.

## §2 Reading drift
Drift is measured against each engine's own early-life baseline.
Deviations beyond ~2 baseline standard deviations sustained over tens
of cycles indicate genuine degradation rather than noise.
""")

(CORPUS / "failure_modes.md").write_text("""# DOC-2 — Turbofan Failure-Mode Signatures
*Compiled project reference for the C-MAPSS fleet. FD001 engines
degrade via HPC (High-Pressure Compressor) efficiency loss.*

## §1 HPC degradation (primary FD001 mode)
Signature: **s_3 up** (HPC outlet temp), **s_7 down** and **s_11 down**
(HPC outlet pressures), **s_9 and s_14 up** (core speeds compensating),
**s_12 up** (fuel flow ratio), **s_4 up** (downstream LPT temp).
Physical cause: blade-tip clearance growth, erosion and fouling reduce
compressor efficiency; the core spools up and burns more fuel to hold
thrust, raising gas-path temperatures.
Risk at end of life: HPC surge/stall margin erosion, downstream
turbine overtemperature.

## §2 Fan-section degradation
Signature: **s_8 and s_13 drift** (fan speeds), **s_15 shift**
(bypass ratio), with core parameters comparatively stable early on.
Physical cause: fan blade erosion/FOD, leading-edge wear.

## §3 Healthy engine
All monitored sensors within ~2 baseline standard deviations, no
sustained monotone drift. No maintenance action indicated; continue
routine condition monitoring.

## §4 Ambiguity rule
If drift is present but weak (<2σ) or non-monotone, classify as
EARLY/UNCERTAIN degradation and recommend increased monitoring
frequency rather than immediate intervention.
""")

(CORPUS / "maintenance_procedures.md").write_text("""# DOC-3 — Maintenance Procedures & Urgency Policy
*Compiled project reference; urgency policy aligned with the fleet's
alerting operating point (alert threshold: predicted RUL below 35
cycles at the chosen 100%-detection operating point).*

## §1 Borescope inspection (HPC)
For suspected HPC degradation: borescope stages 1–3 of the HPC via
designated ports; look for blade-tip wear, leading-edge erosion,
coating loss. Duration ~4h, engine on-wing.
Parts to stage: none (inspection); if wear confirmed -> §3.

## §2 Performance recovery wash
For early-stage efficiency loss (fouling): compressor water wash.
Duration ~2h on-wing. Effective only before mechanical wear dominates.

## §3 HPC module workscope
For confirmed HPC wear at end of life: schedule shop visit; HPC module
exposure, blade/vane replacement as found, clearance restoration.
Parts to stage: HPC blade set (stages per findings), vane segments,
abradable seals. Requires removal — schedule at next opportunity
window when predicted RUL < 35 cycles; IMMEDIATE removal if p10
RUL < 10 cycles.

## §4 Fan workscope
For fan-section degradation: fan blade inspection/lustration,
leading-edge re-profile or blade replacement; balance check.

## §5 Urgency ladder
- **IMMEDIATE** — p10 RUL < 10 cycles: remove from service at next landing.
- **URGENT** — predicted RUL < 35 cycles (alert threshold): schedule §3 within the next maintenance window.
- **PLANNED** — drift confirmed, RUL comfortably above threshold: schedule §1 inspection; consider §2.
- **MONITOR** — weak/uncertain drift (DOC-2 §4): increase monitoring cadence; no intervention.
- **NO ACTION** — healthy (DOC-2 §3).
""")
print(f"wrote {len(list(CORPUS.glob('*.md')))} corpus docs to {CORPUS}/")

# ------------------------------------------------------------------
# 2. per-engine evidence (FD001 test)
# ------------------------------------------------------------------
test = pd.read_csv(RAW / "test_FD001.txt", sep=r"\s+", header=None)
test.columns = COLS

rows = []
for u in sorted(test["unit"].unique()):
    e = test[test["unit"] == u]
    n = len(e)
    base = e.iloc[: max(10, min(30, n // 3))]
    late = e.iloc[-min(20, max(5, n // 4)):]
    rec = {"unit": int(u), "cycles_observed": int(n)}
    for s in SENSORS:
        mu, sd = base[s].mean(), max(base[s].std(), 1e-6)
        drift_sigma = (late[s].mean() - mu) / sd
        # slope over the last 30 cycles (per-cycle, in baseline sigmas)
        tail = e[s].tail(30)
        x = np.arange(len(tail))
        slope = np.polyfit(x, tail.values, 1)[0] / sd if len(tail) > 5 else 0
        rec[f"{s}_drift_sigma"] = round(float(drift_sigma), 2)
        rec[f"{s}_slope_sigma"] = round(float(slope), 3)
    rows.append(rec)

ev = pd.DataFrame(rows)

# join predictions: quantiles (+conformal) and GBM point
qtl = pd.read_parquet(OUT / "test_quantiles.parquet")
ev = ev.merge(qtl, on="unit", how="left")

import lightgbm as lgb
tab = pd.read_parquet(OUT / "fd001_test.parquet")
booster = lgb.Booster(model_file="models/baseline_lgbm_fd001.txt")
X_cols = [c for c in tab.columns
          if c not in ("unit", "rul", "split", "rul_uncapped")]
tab["gbm_rul"] = np.clip(booster.predict(tab[X_cols]), 0, None)
ev = ev.merge(tab[["unit", "gbm_rul"]], on="unit", how="left")

ev.to_parquet(OUT / "engine_evidence.parquet", index=False)
print(f"wrote {OUT}/engine_evidence.parquet "
      f"({len(ev)} engines x {ev.shape[1]} cols)")

# quick sanity: strongest and weakest drifters
ev["max_abs_drift"] = ev[[c for c in ev.columns
                          if c.endswith("_drift_sigma")]].abs().max(axis=1)
print("\nmost degraded (by max |drift|):",
      ev.nlargest(3, "max_abs_drift")[["unit", "max_abs_drift",
                                       "gbm_rul", "rul_true"]]
      .to_string(index=False))
print("\nhealthiest:",
      ev.nsmallest(3, "max_abs_drift")[["unit", "max_abs_drift",
                                        "gbm_rul", "rul_true"]]
      .to_string(index=False))
