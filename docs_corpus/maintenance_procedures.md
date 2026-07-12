# DOC-3 — Maintenance Procedures & Urgency Policy
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
