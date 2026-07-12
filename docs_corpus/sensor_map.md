# DOC-1 — C-MAPSS Turbofan Sensor Map
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
