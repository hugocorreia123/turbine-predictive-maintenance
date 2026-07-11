"""Turbine — Phase 1a: dataset build for FD001.

Produces the canonical tabular dataset every model will share:
  - RUL labels: piecewise-linear, capped at 125 (benchmark convention)
  - features: current value + rolling mean/std/slope (window 30) for
    the 14 kept sensors (conventional 7 flat sensors dropped;
    borderline s_8/s_13 kept — documented choice)
  - canonical split: 80/20 of TRAIN ENGINES (seed 42), persisted —
    split by engine, never by row (row-level splits leak trajectories)
  - test set: features at each test engine's LAST cycle, labels from
    the official RUL_FD001.txt (how published numbers are computed)

Outputs (data/processed/):
  fd001_train.parquet  (with 'split' column: train/val)
  fd001_test.parquet   (one row per engine, official RUL)
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
CAP = 125
WINDOW = 30
RAW = Path("data/raw/CMaps")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

COLS = (["unit", "cycle", "setting_1", "setting_2", "setting_3"]
        + [f"s_{i}" for i in range(1, 22)])
DROP = ["s_1", "s_5", "s_6", "s_10", "s_16", "s_18", "s_19"]
SENSORS = [f"s_{i}" for i in range(1, 22) if f"s_{i}" not in DROP]


def load(name):
    df = pd.read_csv(RAW / name, sep=r"\s+", header=None)
    df.columns = COLS
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Rolling mean/std/slope per sensor, computed within each engine."""
    feats = [df[["unit", "cycle"] + SENSORS].reset_index(drop=True)]
    g = df.groupby("unit")
    for s in SENSORS:
        roll = g[s].rolling(WINDOW, min_periods=1)
        mean = roll.mean().reset_index(level=0, drop=True)
        std = roll.std().reset_index(level=0, drop=True).fillna(0.0)
        slope = mean.groupby(df["unit"]).diff().fillna(0.0)
        feats.append(pd.DataFrame({
            f"{s}_rmean": mean.reset_index(drop=True),
            f"{s}_rstd": std.reset_index(drop=True),
            f"{s}_slope": slope.reset_index(drop=True),
        }))
    return pd.concat(feats, axis=1)


# ---------------- train ----------------
print("building train ...")
train = load("train_FD001.txt")
max_cycle = train.groupby("unit")["cycle"].transform("max")
train["rul"] = np.minimum(max_cycle - train["cycle"], CAP)

Xtr = add_features(train)
Xtr["rul"] = train["rul"].values

rng = np.random.default_rng(SEED)
units = np.sort(train["unit"].unique())
val_units = set(rng.choice(units, size=int(0.2 * len(units)),
                           replace=False))
Xtr["split"] = np.where(Xtr["unit"].isin(list(val_units)), "val", "train")
print(f"  engines: {len(units)}  (val engines: {len(val_units)})")
for s in ["train", "val"]:
    sub = Xtr[Xtr["split"] == s]
    print(f"  {s:<5} rows {len(sub):>6,}  engines "
          f"{sub['unit'].nunique():>3}  rul mean {sub['rul'].mean():.1f}")
Xtr.to_parquet(OUT / "fd001_train.parquet", index=False)

# ---------------- test (last cycle per engine) ----------------
print("building test ...")
test = load("test_FD001.txt")
Xte = add_features(test)
last_idx = test.groupby("unit")["cycle"].idxmax().values
Xte = Xte.loc[last_idx].sort_values("unit").reset_index(drop=True)
rul_true = pd.read_csv(RAW / "RUL_FD001.txt", header=None)[0].values
Xte["rul"] = np.minimum(rul_true, CAP)   # capped, consistent with training
Xte["rul_uncapped"] = rul_true
print(f"  test engines: {len(Xte)}  (evaluated at last available cycle; "
      f"capped-RUL targets)")
Xte.to_parquet(OUT / "fd001_test.parquet", index=False)

n_feats = len(SENSORS) * 4
print(f"\nfeatures per row: {n_feats} "
      f"({len(SENSORS)} sensors x [value, rmean, rstd, slope])")
print(f"wrote {OUT}/fd001_train.parquet, fd001_test.parquet")
