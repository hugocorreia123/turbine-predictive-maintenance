"""Turbine — Phase 2: Temporal CNN (dilated 1-D convolutions) on raw
sensor sequences. TUNED version (window 40, dilations to 16, ch 96,
age channel, lr 5e-4, 120 epochs, patience 25).

Same canonical setup as the baseline, different information diet:
raw windows in, no hand-engineered features. Official FD001 test
protocol (last window per engine vs RUL_FD001.txt, capped).

Outputs: models/tcn_fd001.pt, models/tcn_fd001.json
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=42)
args = ap.parse_args()
SEED = args.seed
CAP = 125
WINDOW = 40
RAW = Path("data/raw/CMaps")
Path("models").mkdir(exist_ok=True)

torch.manual_seed(SEED)
np.random.seed(SEED)

COLS = (["unit", "cycle", "setting_1", "setting_2", "setting_3"]
        + [f"s_{i}" for i in range(1, 22)])
DROP = ["s_1", "s_5", "s_6", "s_10", "s_16", "s_18", "s_19"]
SENSORS = [f"s_{i}" for i in range(1, 22) if f"s_{i}" not in DROP]


def load(name):
    df = pd.read_csv(RAW / name, sep=r"\s+", header=None)
    df.columns = COLS
    return df


def with_age(e, mu, sd):
    """Z-scored sensors + normalized-age channel for one engine."""
    vals = (e[SENSORS].to_numpy(dtype=np.float32, copy=True) - mu) / sd
    age = (e["cycle"].to_numpy(dtype=np.float32) / 300.0)[:, None]
    return np.concatenate([vals, age], axis=1)


def make_windows(df, units, mu, sd):
    X, y = [], []
    for u in units:
        e = df[df["unit"] == u]
        vals = with_age(e, mu, sd)
        rul = e["rul"].to_numpy()
        for end in range(WINDOW, len(e) + 1):
            X.append(vals[end - WINDOW:end])
            y.append(rul[end - 1])
    return (torch.tensor(np.stack(X)).permute(0, 2, 1),  # N,C,T
            torch.tensor(np.array(y), dtype=torch.float32))


print("loading + windowing ...")
train = load("train_FD001.txt")
mx = train.groupby("unit")["cycle"].transform("max")
train["rul"] = np.minimum(mx - train["cycle"], CAP)

rng = np.random.default_rng(SEED)
units = np.sort(train["unit"].unique())
val_units = set(rng.choice(units, size=int(0.2 * len(units)),
                           replace=False))
tr_units = [u for u in units if u not in val_units]

tr_rows = train[train["unit"].isin(tr_units)]
mu = tr_rows[SENSORS].mean().to_numpy(dtype=np.float32)
sd = tr_rows[SENSORS].std().replace(0, 1).to_numpy(dtype=np.float32)

Xtr, ytr = make_windows(train, tr_units, mu, sd)
Xva, yva = make_windows(train, sorted(val_units), mu, sd)
print(f"  train windows {len(Xtr):,}   val windows {len(Xva):,}")

# test: LAST window per engine (left-pad short engines)
test = load("test_FD001.txt")
rul_true = pd.read_csv(RAW / "RUL_FD001.txt", header=None)[0].values
Xte = []
for u in sorted(test["unit"].unique()):
    e = test[test["unit"] == u]
    vals = with_age(e, mu, sd)
    if len(vals) < WINDOW:
        pad = np.repeat(vals[:1], WINDOW - len(vals), axis=0)
        vals = np.concatenate([pad, vals])
    Xte.append(vals[-WINDOW:])
Xte = torch.tensor(np.stack(Xte)).permute(0, 2, 1)
yte = torch.tensor(np.minimum(rul_true, CAP), dtype=torch.float32)
print(f"  test engines {len(Xte)}")


class TCN(nn.Module):
    def __init__(self, c_in=len(SENSORS) + 1, ch=96):
        super().__init__()
        layers, prev = [], c_in
        for d in [1, 2, 4, 8, 16]:
            layers += [nn.Conv1d(prev, ch, kernel_size=3, dilation=d,
                                 padding=d),
                       nn.BatchNorm1d(ch), nn.ReLU(), nn.Dropout(0.2)]
            prev = ch
        self.net = nn.Sequential(*layers)
        self.head = nn.Sequential(nn.AdaptiveAvgPool1d(1), nn.Flatten(),
                                  nn.Linear(ch, 64), nn.ReLU(),
                                  nn.Linear(64, 1))

    def forward(self, x):
        return self.head(self.net(x)).squeeze(-1)


device = (torch.device("mps") if torch.backends.mps.is_available()
          else torch.device("cpu"))
model = TCN().to(device)
print(f"device {device}  params "
      f"{sum(p.numel() for p in model.parameters()):,}")

opt = torch.optim.Adam(model.parameters(), lr=5e-4, weight_decay=1e-5)
sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=120)
loss_fn = nn.MSELoss()

Xva_d, yva_d = Xva.to(device), yva.to(device)
best_val, best_state, bad, patience = 1e9, None, 0, 25
t0 = time.time()

for epoch in range(1, 121):
    model.train()
    perm = torch.randperm(len(Xtr))
    tot = 0.0
    for i in range(0, len(Xtr), 256):
        idx = perm[i:i + 256]
        xb, yb = Xtr[idx].to(device), ytr[idx].to(device)
        opt.zero_grad()
        loss = loss_fn(model(xb), yb)
        loss.backward()
        opt.step()
        tot += loss.item() * len(idx)
    sched.step()

    model.eval()
    with torch.no_grad():
        val_rmse = torch.sqrt(loss_fn(model(Xva_d), yva_d)).item()
    marker = ""
    if val_rmse < best_val:
        best_val, bad = val_rmse, 0
        best_state = {k: v.detach().cpu().clone()
                      for k, v in model.state_dict().items()}
        marker = "  *best*"
    else:
        bad += 1
    print(f"epoch {epoch:>3}  train MSE {tot / len(Xtr):8.2f}  "
          f"val RMSE {val_rmse:6.2f}{marker}")
    if bad >= patience:
        print("early stop")
        break

print(f"training time: {time.time() - t0:.0f}s")
model.load_state_dict(best_state)
model.eval()
with torch.no_grad():
    pt = model(Xte.to(device)).cpu().numpy().clip(0, None)

yt = yte.numpy()
rmse_t = float(np.sqrt(np.mean((pt - yt) ** 2)))
d = pt - yt
nasa = float(np.sum(np.where(d < 0, np.exp(-d / 13) - 1,
                             np.exp(d / 10) - 1)))
late = int(np.sum(pt > yt))

base = json.loads(Path("models/baseline_fd001.json").read_text())
res = {"val_rmse": best_val, "test_rmse": rmse_t,
       "test_nasa_score": nasa, "test_late_predictions": late}

print("\n" + "=" * 56)
print("TCN vs BASELINE — FD001 (official test protocol)")
print("=" * 56)
print(f"{'model':<22}{'test RMSE':>10}{'NASA score':>12}{'late':>6}")
print(f"{'LightGBM (rolled)':<22}{base['test_rmse']:>10.2f}"
      f"{base['test_nasa_score']:>12.0f}"
      f"{base['test_late_predictions']:>6}")
print(f"{'TCN (raw windows)':<22}{rmse_t:>10.2f}{nasa:>12.0f}{late:>6}")
print(f"\npublished FD001 context: classic ML ~16-20, deep ~12-14, "
      f"SOTA ~11-13")

torch.save(best_state, f"models/tcn_fd001_seed{SEED}.pt")
seeds_path = Path("models/tcn_fd001_seeds.json")
allr = json.loads(seeds_path.read_text()) if seeds_path.exists() else {}
allr[str(SEED)] = res
seeds_path.write_text(json.dumps(allr, indent=2))
if len(allr) > 1:
    import statistics as st
    t = [r["test_rmse"] for r in allr.values()]
    v = [r["val_rmse"] for r in allr.values()]
    print(f"\nacross {len(t)} seeds: test RMSE {st.mean(t):.2f} ± "
          f"{st.stdev(t):.2f}  (val {st.mean(v):.2f} ± {st.stdev(v):.2f})")
Path("models/tcn_fd001.json").write_text(json.dumps(res, indent=2))
print(f"wrote models/tcn_fd001_seed{SEED}.pt, tcn_fd001_seeds.json")
