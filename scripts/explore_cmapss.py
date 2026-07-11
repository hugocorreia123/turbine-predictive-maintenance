"""Turbine — Phase 0: first look at C-MAPSS FD001.

Loads the raw whitespace-delimited files, reports trajectory
statistics, identifies flat (uninformative) sensors, and renders the
project's first visual: one engine's sensors drifting toward failure.

Read-only on data; writes docs/degradation_fd001.png.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAW = Path("data/raw/CMaps")
Path("docs").mkdir(exist_ok=True)

COLS = (["unit", "cycle", "setting_1", "setting_2", "setting_3"]
        + [f"s_{i}" for i in range(1, 22)])


def load(name: str) -> pd.DataFrame:
    df = pd.read_csv(RAW / name, sep=r"\s+", header=None)
    df.columns = COLS
    return df


print("=" * 60)
print("TRAIN FD001")
print("=" * 60)
train = load("train_FD001.txt")
print(f"rows: {len(train):,}   engines: {train['unit'].nunique()}")
traj = train.groupby("unit")["cycle"].max()
print(f"trajectory length (cycles to failure): "
      f"min {traj.min()}  median {int(traj.median())}  max {traj.max()}")

test = load("test_FD001.txt")
rul = pd.read_csv(RAW / "RUL_FD001.txt", header=None)[0]
print(f"\nTEST FD001: rows {len(test):,}  engines {test['unit'].nunique()}"
      f"  (truncated trajectories; true RUL given separately: "
      f"min {rul.min()} max {rul.max()})")

# ---------------- flat sensors ----------------
print("\nper-sensor variability (train):")
flat, informative = [], []
for c in [f"s_{i}" for i in range(1, 22)]:
    sd = train[c].std()
    rel = sd / (abs(train[c].mean()) + 1e-9)
    tag = "FLAT" if sd < 1e-6 or rel < 1e-4 else ""
    (flat if tag else informative).append(c)
    print(f"  {c:<5} std={sd:12.6f}  {tag}")
print(f"\nflat sensors (drop later): {flat}")
print(f"informative sensors: {len(informative)}")

# ---------------- operating settings ----------------
print("\noperating settings (FD001 should be ~single condition):")
for c in ["setting_1", "setting_2", "setting_3"]:
    print(f"  {c}: min {train[c].min():.4f}  max {train[c].max():.4f}  "
          f"unique(rounded 2dp) {train[c].round(2).nunique()}")

# ---------------- degradation plot ----------------
unit = traj.idxmax()  # longest-lived engine tells the clearest story
e = train[train["unit"] == unit]
show = ["s_2", "s_3", "s_4", "s_7", "s_11", "s_15"]  # known-informative set
fig, axes = plt.subplots(2, 3, figsize=(13, 6), sharex=True)
for ax, c in zip(axes.flat, show):
    ax.plot(e["cycle"], e[c], lw=0.8, color="#1f3864")
    # smoothed trend
    ax.plot(e["cycle"], e[c].rolling(15, min_periods=1).mean(),
            lw=2.0, color="#d62728")
    ax.set_title(c, fontsize=10)
    ax.axvline(e["cycle"].max(), color="black", lw=1, ls="--", alpha=0.6)
fig.suptitle(
    f"C-MAPSS FD001 — engine {unit}: sensors drifting toward failure "
    f"(dashed line = failure at cycle {e['cycle'].max()})",
    fontsize=12)
fig.supxlabel("operating cycle")
fig.tight_layout()
fig.savefig("docs/degradation_fd001.png", dpi=150)
print(f"\nwrote docs/degradation_fd001.png (engine {unit}, "
      f"{e['cycle'].max()} cycles)")
