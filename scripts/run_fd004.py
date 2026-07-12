"""Turbine — Phase 5: FD004, the hard benchmark. CPU-SAFE version.

Six operating conditions, two fault modes, 249/248 engines. The known
trap: sensors shift with operating condition, so global normalization
teaches the model operating modes instead of health. Fix:
PER-CONDITION normalization (KMeans k=6 on the settings, fit on train;
z-score sensors within each condition).

Crash-proofing (lessons from the MPS wedge):
  - CPU only, always (MPS deadlocked twice on this workload)
  - small model (ch=64), 30-epoch budget, batch 512
  - RESUMABLE: each seed's result is appended to
    models/fd004_results.json as it finishes; rerunning skips
    finished seeds. The GBM result is also cached.
  - run detached:  nohup uv run python scripts/run_fd004.py > fd004.log 2>&1 &
    watch:         tail -f fd004.log

Published FD004 context (test RMSE): classic ML ~28-35,
deep sequence models ~19-24, SOTA ~16-20.
"""

import json
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.cluster import KMeans

CAP = 125
WINDOW = 40
SEEDS = [42, 43, 44]
RAW = Path("data/raw/CMaps")
RES_PATH = Path("models/fd004_results.json")
Path("models").mkdir(exist_ok=True)

COLS = (["unit", "cycle", "setting_1", "setting_2", "setting_3"]
        + [f"s_{i}" for i in range(1, 22)])
DROP = ["s_1", "s_5", "s_6", "s_10", "s_16", "s_18", "s_19"]
SENSORS = [f"s_{i}" for i in range(1, 22) if f"s_{i}" not in DROP]
SETTINGS = ["setting_1", "setting_2", "setting_3"]

device = torch.device("cpu")
torch.set_num_threads(max(1, (torch.get_num_threads() or 8)))
print(f"device: {device}")

results = json.loads(RES_PATH.read_text()) if RES_PATH.exists() else {}


def save():
    RES_PATH.write_text(json.dumps(results, indent=2))


def load(name):
    df = pd.read_csv(RAW / name, sep=r"\s+", header=None)
    df.columns = COLS
    return df


def rmse(y, p):
    return float(np.sqrt(np.mean((p - y) ** 2)))


def nasa(y, p):
    d = p - y
    return float(np.sum(np.where(d < 0, np.exp(-d / 13) - 1,
                                 np.exp(d / 10) - 1)))


print("loading FD004 ...", flush=True)
train = load("train_FD004.txt")
test = load("test_FD004.txt")
rul_true = pd.read_csv(RAW / "RUL_FD004.txt", header=None)[0].values
mx = train.groupby("unit")["cycle"].transform("max")
train["rul"] = np.minimum(mx - train["cycle"], CAP)
yte = np.minimum(rul_true, CAP).astype(np.float32)
print(f"  train: {train['unit'].nunique()} engines, {len(train):,} rows"
      f"   test: {test['unit'].nunique()} engines", flush=True)

# ---------------- per-condition normalization ----------------
km = KMeans(n_clusters=6, n_init=10, random_state=42)
train["cond"] = km.fit_predict(train[SETTINGS])
test["cond"] = km.predict(test[SETTINGS])
print(f"  condition cluster sizes (train): "
      f"{np.bincount(train['cond']).tolist()}", flush=True)

stats = train.groupby("cond")[SENSORS].agg(["mean", "std"])
for s in SENSORS:
    mu = train["cond"].map(stats[(s, "mean")])
    sd = train["cond"].map(stats[(s, "std")]).replace(0, 1)
    train[s] = (train[s] - mu) / sd
    mu_t = test["cond"].map(stats[(s, "mean")])
    sd_t = test["cond"].map(stats[(s, "std")]).replace(0, 1)
    test[s] = (test[s] - mu_t) / sd_t

rng = np.random.default_rng(42)
units = np.sort(train["unit"].unique())

# ================= GBM on rolled features (cached) =================
if "gbm" in results:
    print(f"\nGBM cached: RMSE {results['gbm']['test_rmse']:.2f}",
          flush=True)
else:
    print("\nGBM baseline ...", flush=True)

    def rolled(df):
        feats = [df[["unit", "cycle"] + SENSORS].reset_index(drop=True)]
        g = df.groupby("unit")
        for s in SENSORS:
            roll = g[s].rolling(30, min_periods=1)
            mean = roll.mean().reset_index(level=0, drop=True)
            std = roll.std().reset_index(level=0, drop=True).fillna(0.0)
            slope = mean.groupby(df["unit"]).diff().fillna(0.0)
            feats.append(pd.DataFrame({
                f"{s}_rmean": mean.reset_index(drop=True),
                f"{s}_rstd": std.reset_index(drop=True),
                f"{s}_slope": slope.reset_index(drop=True)}))
        return pd.concat(feats, axis=1)

    Xtab = rolled(train)
    Xtab["rul"] = train["rul"].values
    val_units_g = set(rng.choice(units, size=int(0.2 * len(units)),
                                 replace=False))
    is_val = Xtab["unit"].isin(list(val_units_g))
    X_cols = [c for c in Xtab.columns if c not in ("unit", "rul")]

    gbm = lgb.LGBMRegressor(n_estimators=3000, learning_rate=0.03,
                            num_leaves=63, min_child_samples=50,
                            colsample_bytree=0.8, subsample=0.8,
                            subsample_freq=1, random_state=42, n_jobs=-1)
    gbm.fit(Xtab.loc[~is_val, X_cols], Xtab.loc[~is_val, "rul"],
            eval_set=[(Xtab.loc[is_val, X_cols],
                       Xtab.loc[is_val, "rul"])],
            eval_metric="rmse",
            callbacks=[lgb.early_stopping(200, verbose=False)])
    Xtab_te = rolled(test)
    last = test.groupby("unit")["cycle"].idxmax().values
    Xte_tab = Xtab_te.loc[last].sort_values("unit")
    p_gbm = np.clip(gbm.predict(Xte_tab[X_cols]), 0, None)
    results["gbm"] = {"test_rmse": rmse(yte, p_gbm),
                      "test_nasa": nasa(yte, p_gbm)}
    save()
    print(f"  GBM test RMSE {results['gbm']['test_rmse']:.2f}  "
          f"NASA {results['gbm']['test_nasa']:.0f}", flush=True)


# ================= TCN (CPU-sized), resumable per seed =============
def with_age(e):
    vals = e[SENSORS].to_numpy(dtype=np.float32, copy=True)
    age = (e["cycle"].to_numpy(dtype=np.float32) / 400.0)[:, None]
    return np.concatenate([vals, age], axis=1)


def make_windows(df, units_):
    X, y = [], []
    for u in units_:
        e = df[df["unit"] == u]
        vals = with_age(e)
        rul = e["rul"].to_numpy()
        for end in range(WINDOW, len(e) + 1):
            X.append(vals[end - WINDOW:end])
            y.append(rul[end - 1])
    return (torch.tensor(np.stack(X)).permute(0, 2, 1),
            torch.tensor(np.array(y), dtype=torch.float32))


class TCN(nn.Module):
    def __init__(self, c_in=len(SENSORS) + 1, ch=64):
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


# test windows (built once)
Xte_list = []
for u in sorted(test["unit"].unique()):
    e = test[test["unit"] == u]
    vals = with_age(e)
    if len(vals) < WINDOW:
        vals = np.concatenate(
            [np.repeat(vals[:1], WINDOW - len(vals), axis=0), vals])
    Xte_list.append(vals[-WINDOW:])
Xte = torch.tensor(np.stack(Xte_list)).permute(0, 2, 1)

seeds_done = results.get("tcn_per_seed", {})
for seed in SEEDS:
    if str(seed) in seeds_done:
        print(f"\nseed {seed}: cached "
              f"(test RMSE {seeds_done[str(seed)]['test_rmse']:.2f})",
              flush=True)
        continue
    print(f"\nTCN seed {seed} ...", flush=True)
    torch.manual_seed(seed)
    np.random.seed(seed)
    srng = np.random.default_rng(seed)
    val_u = set(srng.choice(units, size=int(0.2 * len(units)),
                            replace=False))
    tr_u = [u for u in units if u not in val_u]
    Xtr, ytr = make_windows(train, tr_u)
    Xva, yva = make_windows(train, sorted(val_u))
    print(f"  windows: train {len(Xtr):,}  val {len(Xva):,}", flush=True)

    model = TCN().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=5e-4,
                           weight_decay=1e-5)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=30)
    loss_fn = nn.MSELoss()
    best_val, best_state, bad = 1e9, None, 0
    t0 = time.time()
    for epoch in range(1, 31):
        model.train()
        perm = torch.randperm(len(Xtr))
        for i in range(0, len(Xtr), 512):
            idx = perm[i:i + 512]
            opt.zero_grad()
            loss_fn(model(Xtr[idx]), ytr[idx]).backward()
            opt.step()
        sched.step()
        model.eval()
        with torch.no_grad():
            v = torch.sqrt(loss_fn(model(Xva), yva)).item()
        marker = ""
        if v < best_val:
            best_val, bad = v, 0
            best_state = {k: t.detach().cpu().clone()
                          for k, t in model.state_dict().items()}
            marker = " *best*"
        else:
            bad += 1
        print(f"  epoch {epoch:>2}  val RMSE {v:6.2f}  "
              f"({time.time() - t0:.0f}s){marker}", flush=True)
        if bad >= 8:
            print("  early stop", flush=True)
            break

    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        p = model(Xte).numpy().clip(0, None)
    r = rmse(yte, p)
    seeds_done[str(seed)] = {
        "val_rmse": best_val, "test_rmse": r,
        "test_nasa": nasa(yte, p),
        "seconds": round(time.time() - t0),
        "preds": [float(x) for x in p],
    }
    results["tcn_per_seed"] = seeds_done
    save()
    print(f"  seed {seed} DONE: test RMSE {r:.2f}  "
          f"({seeds_done[str(seed)]['seconds']}s)", flush=True)

# ================= summary =================
rmses = [s["test_rmse"] for s in seeds_done.values()]
preds = np.array([s["preds"] for s in seeds_done.values()])
ens = preds.mean(axis=0)
results["tcn_summary"] = {
    "n_seeds": len(rmses),
    "test_rmse_mean": float(np.mean(rmses)),
    "test_rmse_std": float(np.std(rmses, ddof=1)) if len(rmses) > 1 else 0.0,
    "ensemble_test_rmse": rmse(yte, ens),
    "ensemble_test_nasa": nasa(yte, ens),
}
save()

print("\n" + "=" * 56)
print("FD004 — FINAL COMPARISON (official protocol)")
print("=" * 56)
print(f"{'model':<26}{'test RMSE':>12}{'NASA':>10}")
print(f"{'LightGBM (rolled)':<26}{results['gbm']['test_rmse']:>12.2f}"
      f"{results['gbm']['test_nasa']:>10.0f}")
if len(rmses) > 1:
    print(f"{'TCN single (' + str(len(rmses)) + ' seeds)':<26}"
          f"{np.mean(rmses):>9.2f} ±{np.std(rmses, ddof=1):.2f}")
else:
    print(f"{'TCN single (1 seed)':<26}{rmses[0]:>12.2f}")
print(f"{'TCN ensemble':<26}"
      f"{results['tcn_summary']['ensemble_test_rmse']:>12.2f}"
      f"{results['tcn_summary']['ensemble_test_nasa']:>10.0f}")
print("\npublished FD004 context: classic ML ~28-35, deep ~19-24, "
      "SOTA ~16-20")
print("wrote models/fd004_results.json")
