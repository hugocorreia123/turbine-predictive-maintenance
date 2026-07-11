"""Turbine — Phase 2b: 5-seed TCN deep ensemble on FD001.

Loads the five per-seed checkpoints, averages their test predictions,
and reports ensemble RMSE / NASA score vs the single-model mean and
the GBM baseline. Deep ensembles are the standard variance-reduction
(and uncertainty) move; if the ensemble beats the baseline, the honest
claim is "the ensemble wins; a single TCN does not."
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

CAP = 125
WINDOW = 40
SEEDS = [42, 43, 44, 45, 46]
RAW = Path("data/raw/CMaps")

COLS = (["unit", "cycle", "setting_1", "setting_2", "setting_3"]
        + [f"s_{i}" for i in range(1, 22)])
DROP = ["s_1", "s_5", "s_6", "s_10", "s_16", "s_18", "s_19"]
SENSORS = [f"s_{i}" for i in range(1, 22) if f"s_{i}" not in DROP]


def load(name):
    df = pd.read_csv(RAW / name, sep=r"\s+", header=None)
    df.columns = COLS
    return df


def with_age(e, mu, sd):
    vals = (e[SENSORS].to_numpy(dtype=np.float32, copy=True) - mu) / sd
    age = (e["cycle"].to_numpy(dtype=np.float32) / 300.0)[:, None]
    return np.concatenate([vals, age], axis=1)


class TCN(nn.Module):
    def __init__(self, c_in=len(SENSORS) + 1, ch=96):
        super().__init__()
        layers, prev = [], c_in
        for d in [1, 2, 4, 8, 16]:
            layers += [nn.Conv1d(prev, ch, 3, dilation=d, padding=d),
                       nn.BatchNorm1d(ch), nn.ReLU(), nn.Dropout(0.2)]
            prev = ch
        self.net = nn.Sequential(*layers)
        self.head = nn.Sequential(nn.AdaptiveAvgPool1d(1), nn.Flatten(),
                                  nn.Linear(ch, 64), nn.ReLU(),
                                  nn.Linear(64, 1))

    def forward(self, x):
        return self.head(self.net(x)).squeeze(-1)


# ---- normalization stats must match training (train engines, seed 42
#      split is irrelevant here: stats were computed per-run on that
#      run's train engines; for the ensemble we recompute per seed) ----
train = load("train_FD001.txt")
test = load("test_FD001.txt")
rul_true = pd.read_csv(RAW / "RUL_FD001.txt", header=None)[0].values
yte = np.minimum(rul_true, CAP).astype(np.float32)

device = (torch.device("mps") if torch.backends.mps.is_available()
          else torch.device("cpu"))

preds = []
units_all = np.sort(train["unit"].unique())
for seed in SEEDS:
    rng = np.random.default_rng(seed)
    val_units = set(rng.choice(units_all,
                               size=int(0.2 * len(units_all)),
                               replace=False))
    tr_rows = train[~train["unit"].isin(val_units)]
    mu = tr_rows[SENSORS].mean().to_numpy(dtype=np.float32)
    sd = tr_rows[SENSORS].std().replace(0, 1).to_numpy(dtype=np.float32)

    Xte = []
    for u in sorted(test["unit"].unique()):
        e = test[test["unit"] == u]
        vals = with_age(e, mu, sd)
        if len(vals) < WINDOW:
            vals = np.concatenate(
                [np.repeat(vals[:1], WINDOW - len(vals), axis=0), vals])
        Xte.append(vals[-WINDOW:])
    Xte = torch.tensor(np.stack(Xte)).permute(0, 2, 1).to(device)

    model = TCN().to(device)
    model.load_state_dict(torch.load(f"models/tcn_fd001_seed{seed}.pt",
                                     map_location=device))
    model.eval()
    with torch.no_grad():
        p = model(Xte).cpu().numpy().clip(0, None)
    preds.append(p)
    rm = float(np.sqrt(np.mean((p - yte) ** 2)))
    print(f"seed {seed}: test RMSE {rm:.2f}")

ens = np.mean(preds, axis=0)
rmse = float(np.sqrt(np.mean((ens - yte) ** 2)))
d = ens - yte
nasa = float(np.sum(np.where(d < 0, np.exp(-d / 13) - 1,
                             np.exp(d / 10) - 1)))
late = int(np.sum(ens > yte))

base = json.loads(Path("models/baseline_fd001.json").read_text())
seeds = json.loads(Path("models/tcn_fd001_seeds.json").read_text())
tests = [r["test_rmse"] for r in seeds.values()]

print("\n" + "=" * 56)
print("FD001 — FINAL COMPARISON (official protocol)")
print("=" * 56)
print(f"{'model':<28}{'test RMSE':>10}{'NASA':>8}")
print(f"{'LightGBM (rolled feats)':<28}{base['test_rmse']:>10.2f}"
      f"{base['test_nasa_score']:>8.0f}")
print(f"{'TCN single (5-seed mean)':<28}"
      f"{np.mean(tests):>7.2f} ±{np.std(tests, ddof=1):.2f}"
      f"{'':>8}")
print(f"{'TCN 5-seed ENSEMBLE':<28}{rmse:>10.2f}{nasa:>8.0f}")
print(f"\nlate predictions (ensemble): {late}/100")

Path("models/tcn_ensemble_fd001.json").write_text(json.dumps(
    {"test_rmse": rmse, "test_nasa_score": nasa,
     "test_late_predictions": late,
     "single_model_mean": float(np.mean(tests)),
     "single_model_std": float(np.std(tests, ddof=1))}, indent=2))
print("wrote models/tcn_ensemble_fd001.json")
