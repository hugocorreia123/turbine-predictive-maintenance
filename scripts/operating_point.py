"""Turbine — Phase 4: alerting operating point.

Policy: flag an engine for maintenance when its predicted RUL drops
below a threshold T. We compare two policies on the 100 official test
engines:

  RISK-AVERSE : flag if conformal p10 < T   (quantile TCN + CQR)
  POINT       : flag if GBM point prediction < T

Definitions (H = attention horizon, 30 cycles):
  needs attention  = true RUL < H
  detection rate   = flagged among needs-attention engines
  false-alarm rate = flagged among healthy engines (true RUL >= H)
  lead time        = mean true RUL among correctly flagged engines
                     (how many cycles of warning maintenance gets)

Also translates one chosen operating point into an illustrative,
assumption-labeled € story.

Outputs: models/operating_point_fd001.json + console tables
"""

import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

H = 30                      # cycles: "needs attention" horizon
THRESHOLDS = [10, 15, 20, 25, 30, 35, 40]

# --- illustrative cost assumptions (clearly labeled) ---
COST_UNPLANNED = 250_000    # EUR per unplanned failure event
COST_PLANNED = 60_000       # EUR per planned early intervention
COST_INSPECTION = 8_000     # EUR per false-alarm inspection

q = pd.read_parquet("data/processed/test_quantiles.parquet")
y = q["rul_true"].values
p10c = q["p10_conf"].values

# GBM point predictions on the same engines
test_tab = pd.read_parquet("data/processed/fd001_test.parquet")
booster = lgb.Booster(model_file="models/baseline_lgbm_fd001.txt")
X_cols = [c for c in test_tab.columns
          if c not in ("unit", "rul", "split", "rul_uncapped")]
gbm = np.clip(booster.predict(test_tab[X_cols]), 0, None)

needs = y < H
n_needs, n_healthy = int(needs.sum()), int((~needs).sum())
print(f"test engines: {len(y)}   needs-attention (RUL<{H}): {n_needs}   "
      f"healthy: {n_healthy}")


def evaluate(scores, name):
    rows = []
    print(f"\n{name}")
    print(f"{'T':>4} | {'detection':>9} | {'false alarms':>12} | "
          f"{'lead time':>9}")
    print("-" * 46)
    for T in THRESHOLDS:
        flag = scores < T
        det = float((flag & needs).sum() / max(n_needs, 1))
        fa = float((flag & ~needs).sum() / max(n_healthy, 1))
        lead = float(y[flag & needs].mean()) if (flag & needs).any() else 0
        rows.append({"threshold": T, "detection": det,
                     "false_alarm_rate": fa, "mean_lead_time": lead})
        print(f"{T:>4} | {det:>8.0%} | {fa:>11.1%} | {lead:>7.1f}c")
    return rows


res_p10 = evaluate(p10c, "RISK-AVERSE policy (conformal p10 < T)")
res_gbm = evaluate(gbm, "POINT policy (GBM prediction < T)")


# ---------------- chosen operating point + EUR framing ----------------
def pick(rows):
    """Smallest T reaching >= 90% detection."""
    for r in rows:
        if r["detection"] >= 0.90:
            return r
    return rows[-1]


op_p10 = pick(res_p10)
op_gbm = pick(res_gbm)

print("\n" + "=" * 56)
print("CHOSEN OPERATING POINTS (first T with >=90% detection)")
print("=" * 56)
for name, op in [("risk-averse p10", op_p10), ("point GBM", op_gbm)]:
    print(f"{name:<16} T={op['threshold']:<3} detection "
          f"{op['detection']:.0%}  false alarms "
          f"{op['false_alarm_rate']:.1%}  lead {op['mean_lead_time']:.1f}c")

# EUR framing on the p10 operating point
det, fa = op_p10["detection"], op_p10["false_alarm_rate"]
caught = det * n_needs
missed = (1 - det) * n_needs
false_alarms = fa * n_healthy
savings = (caught * (COST_UNPLANNED - COST_PLANNED)
           - false_alarms * COST_INSPECTION)
print("\nILLUSTRATIVE EUR (assumptions: unplanned 250K, planned 60K, "
      "inspection 8K):")
print(f"  per {len(y)} assets: {caught:.0f} failures converted from "
      f"unplanned to planned, {missed:.0f} missed, "
      f"{false_alarms:.0f} false-alarm inspections")
print(f"  net saving ~= EUR {savings:,.0f} vs run-to-failure "
      f"(assumption-labeled scaling, not a claim about any operator)")

Path("models/operating_point_fd001.json").write_text(json.dumps(
    {"horizon": H, "risk_averse_p10": res_p10, "point_gbm": res_gbm,
     "chosen_p10": op_p10, "chosen_gbm": op_gbm,
     "cost_assumptions": {"unplanned": COST_UNPLANNED,
                          "planned": COST_PLANNED,
                          "inspection": COST_INSPECTION},
     "illustrative_net_saving_eur": savings}, indent=2))
print("\nwrote models/operating_point_fd001.json")
