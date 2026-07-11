"""Turbine — Phase 3: probabilistic RUL via quantile regression,
with conformal calibration (CQR).

Same TCN backbone as Phase 2, head outputs THREE quantiles
(p10 / p50 / p90) trained with pinball loss. Raw quantile nets often
under-cover, so the p10-p90 band is conformally calibrated on the
validation engines (CQR): expand the band by the smallest q_hat such
that 80% of val targets are covered, then apply that fixed correction
to test. Distribution-free, honest.

Outputs: models/tcn_quantile_fd001.pt, models/tcn_quantile_fd001.json,
         docs/calibration_fd001.png,
         data/processed/test_quantiles.parquet (for Phase 4 alerting)
"""

import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

SEED = 42
CAP = 125
WINDOW = 40
QUANTILES = [0.1, 0.5, 0.9]
TARGET_COVERAGE = 0.8
RAW = Path("data/raw/CMaps")
Path("models").mkdir(exist_ok=True)
Path("docs").mkdir(exist_ok=True)

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
    return (torch.tensor(np.stack(X)).permute(0, 2, 1),
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

test = load("test_FD001.txt")
rul_true = pd.read_csv(RAW / "RUL_FD001.txt", header=None)[0].values
Xte, te_units = [], []
for u in sorted(test["unit"].unique()):
    e = test[test["unit"] == u]
    vals = with_age(e, mu, sd)
    if len(vals) < WINDOW:
        vals = np.concatenate(
            [np.repeat(vals[:1], WINDOW - len(vals), axis=0), vals])
    Xte.append(vals[-WINDOW:])
    te_units.append(u)
Xte = torch.tensor(np.stack(Xte)).permute(0, 2, 1)
yte = np.minimum(rul_true, CAP).astype(np.float32)
print(f"  test engines {len(Xte)}")


class TCNQ(nn.Module):
    def __init__(self, c_in=len(SENSORS) + 1, ch=96, n_q=len(QUANTILES)):
        super().__init__()
        layers, prev = [], c_in
        for d in [1, 2, 4, 8, 16]:
            layers += [nn.Conv1d(prev, ch, 3, dilation=d, padding=d),
                       nn.BatchNorm1d(ch), nn.ReLU(), nn.Dropout(0.2)]
            prev = ch
        self.net = nn.Sequential(*layers)
        self.head = nn.Sequential(nn.AdaptiveAvgPool1d(1), nn.Flatten(),
                                  nn.Linear(ch, 64), nn.ReLU(),
                                  nn.Linear(64, n_q))

    def forward(self, x):
        return self.head(self.net(x))  # N x 3


def pinball(pred, y):
    losses = []
    for i, q in enumerate(QUANTILES):
        e = y - pred[:, i]
        losses.append(torch.maximum(q * e, (q - 1) * e).mean())
    return torch.stack(losses).mean()


device = (torch.device("mps") if torch.backends.mps.is_available()
          else torch.device("cpu"))
model = TCNQ().to(device)
print(f"device {device}  params "
      f"{sum(p.numel() for p in model.parameters()):,}")

opt = torch.optim.Adam(model.parameters(), lr=5e-4, weight_decay=1e-5)
sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=120)

Xva_d, yva_d = Xva.to(device), yva.to(device)
best_val, best_state, bad, patience = 1e9, None, 0, 25
t0 = time.time()

for epoch in range(1, 121):
    model.train()
    perm = torch.randperm(len(Xtr))
    for i in range(0, len(Xtr), 256):
        idx = perm[i:i + 256]
        xb, yb = Xtr[idx].to(device), ytr[idx].to(device)
        opt.zero_grad()
        loss = pinball(model(xb), yb)
        loss.backward()
        opt.step()
    sched.step()

    model.eval()
    with torch.no_grad():
        val_loss = pinball(model(Xva_d), yva_d).item()
    marker = ""
    if val_loss < best_val:
        best_val, bad = val_loss, 0
        best_state = {k: v.detach().cpu().clone()
                      for k, v in model.state_dict().items()}
        marker = "  *best*"
    else:
        bad += 1
    if epoch % 5 == 0 or marker:
        print(f"epoch {epoch:>3}  val pinball {val_loss:6.3f}{marker}")
    if bad >= patience:
        print("early stop")
        break

print(f"training time: {time.time() - t0:.0f}s")
model.load_state_dict(best_state)
model.eval()
with torch.no_grad():
    q_te = model(Xte.to(device)).cpu().numpy()
    q_va = model(Xva_d).cpu().numpy()

# enforce non-crossing quantiles at inference
q_te = np.sort(q_te, axis=1).clip(0, None)
q_va = np.sort(q_va, axis=1).clip(0, None)
p10, p50, p90 = q_te[:, 0], q_te[:, 1], q_te[:, 2]

# ---------------- conformal calibration (CQR) on val ----------------
yva_np = yva.numpy()
E = np.maximum(q_va[:, 0] - yva_np, yva_np - q_va[:, 2])
k = min(int(np.ceil(TARGET_COVERAGE * (len(E) + 1))) - 1, len(E) - 1)
q_hat = float(np.sort(E)[k])
p10c = (p10 - q_hat).clip(0, None)
p90c = p90 + q_hat

# ---------------- metrics ----------------
rmse_p50 = float(np.sqrt(np.mean((p50 - yte) ** 2)))
d = p50 - yte
nasa = float(np.sum(np.where(d < 0, np.exp(-d / 13) - 1,
                             np.exp(d / 10) - 1)))
cov_raw = float(np.mean((yte >= p10) & (yte <= p90)))
cov_va = float(np.mean((yva_np >= q_va[:, 0]) & (yva_np <= q_va[:, 2])))
cov_conf = float(np.mean((yte >= p10c) & (yte <= p90c)))
width_raw = float(np.mean(p90 - p10))
width_conf = float(np.mean(p90c - p10c))

point = json.loads(Path("models/tcn_fd001.json").read_text())
res = {"test_rmse_p50": rmse_p50, "test_nasa_score_p50": nasa,
       "test_coverage_raw": cov_raw, "val_coverage_raw": cov_va,
       "conformal_adjustment": q_hat,
       "test_coverage_conformal": cov_conf,
       "mean_interval_width_raw": width_raw,
       "mean_interval_width_conformal": width_conf}

print("\n" + "=" * 56)
print("QUANTILE TCN + CQR — FD001")
print("=" * 56)
print(f"p50 test RMSE:          {rmse_p50:.2f}   "
      f"(point TCN: {point['test_rmse']:.2f})")
print(f"p50 NASA score:         {nasa:.0f}    "
      f"(point TCN: {point['test_nasa_score']:.0f})")
print(f"coverage RAW val/test:  {cov_va:.1%} / {cov_raw:.1%}   "
      f"(target ~80%)")
print(f"conformal adjustment:   +/-{q_hat:.1f} cycles")
print(f"coverage CONFORMAL:     {cov_conf:.1%}   (target ~80%)")
print(f"interval width raw/conf:{width_raw:.1f} / {width_conf:.1f} cycles")

# ---------------- plots ----------------
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
order = np.argsort(yte)
ax = axes[0]
x = np.arange(len(yte))
ax.fill_between(x, p10c[order], p90c[order], alpha=0.3, color="#1f3864",
                label="conformal p10–p90")
ax.plot(x, p50[order], lw=1.4, color="#1f3864", label="p50 prediction")
ax.plot(x, yte[order], lw=1.2, color="#d62728", label="true RUL")
ax.set_xlabel("test engines (sorted by true RUL)")
ax.set_ylabel("RUL (cycles)")
ax.set_title(f"Prediction intervals — conformal coverage {cov_conf:.0%}")
ax.legend()

ax = axes[1]
emp = [float(np.mean(yte <= p10)), float(np.mean(yte <= p50)),
       float(np.mean(yte <= p90))]
ax.plot([0, 1], [0, 1], "k--", lw=1, label="perfect calibration")
ax.scatter(QUANTILES, emp, s=80, color="#d62728", zorder=3,
           label="empirical (raw quantiles)")
for q, e_ in zip(QUANTILES, emp):
    ax.annotate(f"q{int(q * 100)}: {e_:.2f}", (q, e_),
                textcoords="offset points", xytext=(8, -4), fontsize=9)
ax.set_xlabel("nominal quantile")
ax.set_ylabel("empirical fraction below")
ax.set_title("Reliability (before conformal correction)")
ax.legend()
fig.suptitle("Turbine — probabilistic RUL calibration (FD001 test)")
fig.tight_layout()
fig.savefig("docs/calibration_fd001.png", dpi=150)
print("wrote docs/calibration_fd001.png")

torch.save(best_state, "models/tcn_quantile_fd001.pt")
Path("models/tcn_quantile_fd001.json").write_text(
    json.dumps(res, indent=2))
pd.DataFrame({"unit": te_units, "rul_true": yte,
              "p10": p10, "p50": p50, "p90": p90,
              "p10_conf": p10c, "p90_conf": p90c}).to_parquet(
    "data/processed/test_quantiles.parquet", index=False)
print("wrote models/tcn_quantile_fd001.pt, models/tcn_quantile_fd001.json, "
      "data/processed/test_quantiles.parquet")
