"""Turbine — Phase 1b: LightGBM RUL baseline.

The honest control the deep model must beat. Trains on the canonical
engine-level split, early-stops on val RMSE, and reports on the
OFFICIAL test protocol (last cycle per test engine vs RUL_FD001.txt).

Metrics:
  - RMSE (standard comparison metric in the C-MAPSS literature)
  - NASA scoring function: sum of exp(-d/13)-1 for early (d<0) and
    exp(d/10)-1 for late (d>0) predictions, d = pred - true.
    Asymmetric on purpose: predicting failure LATE is penalized
    harder than early, because a missed failure costs more than an
    early inspection.

Published context on FD001 (test RMSE): classic ML ~16-20,
deep sequence models ~12-14, state-of-the-art ~11-13.

Outputs: models/baseline_lgbm_fd001.txt, models/baseline_fd001.json
"""

import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

SEED = 42
Path("models").mkdir(exist_ok=True)

train = pd.read_parquet("data/processed/fd001_train.parquet")
test = pd.read_parquet("data/processed/fd001_test.parquet")

drop = ["unit", "rul", "split", "rul_uncapped"]
X_cols = [c for c in train.columns if c not in drop]
print(f"{len(X_cols)} features")

tr = train[train["split"] == "train"]
va = train[train["split"] == "val"]

model = lgb.LGBMRegressor(
    n_estimators=3000,
    learning_rate=0.03,
    num_leaves=63,
    min_child_samples=50,
    colsample_bytree=0.8,
    subsample=0.8,
    subsample_freq=1,
    random_state=SEED,
    n_jobs=-1,
)
model.fit(
    tr[X_cols], tr["rul"],
    eval_set=[(va[X_cols], va["rul"])],
    eval_metric="rmse",
    callbacks=[lgb.early_stopping(200, verbose=True),
               lgb.log_evaluation(200)],
)


def rmse(y, p):
    return float(np.sqrt(np.mean((p - y) ** 2)))


def nasa_score(y, p):
    d = p - y
    return float(np.sum(np.where(d < 0,
                                 np.exp(-d / 13.0) - 1.0,
                                 np.exp(d / 10.0) - 1.0)))


metrics = {"best_iteration": int(model.best_iteration_ or 0)}

pv = np.clip(model.predict(va[X_cols]), 0, None)
metrics["val_rmse"] = rmse(va["rul"].values, pv)

pt = np.clip(model.predict(test[X_cols]), 0, None)
yt = test["rul"].values
metrics["test_rmse"] = rmse(yt, pt)
metrics["test_nasa_score"] = nasa_score(yt, pt)
metrics["test_mae"] = float(np.mean(np.abs(pt - yt)))
late = int(np.sum(pt > yt))
metrics["test_late_predictions"] = late  # engines predicted healthier than reality

print("\n" + "=" * 56)
print("BASELINE RESULTS (LightGBM, rolled features) — FD001")
print("=" * 56)
print(f"val  RMSE:        {metrics['val_rmse']:.2f}")
print(f"test RMSE:        {metrics['test_rmse']:.2f}   "
      f"(published: classic ML ~16-20, deep ~12-14, SOTA ~11-13)")
print(f"test NASA score:  {metrics['test_nasa_score']:.0f}   (lower = better)")
print(f"test MAE:         {metrics['test_mae']:.2f}")
print(f"late predictions: {late}/100 engines predicted healthier than "
      f"they are (the dangerous direction)")

print("\ntop 10 features:")
imp = pd.Series(model.feature_importances_, index=X_cols)
for name, v in imp.sort_values(ascending=False).head(10).items():
    print(f"  {name:<14} {v}")

model.booster_.save_model("models/baseline_lgbm_fd001.txt")
Path("models/baseline_fd001.json").write_text(json.dumps(metrics, indent=2))
print("\nwrote models/baseline_lgbm_fd001.txt, models/baseline_fd001.json")
