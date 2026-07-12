# DOC-2 — Turbofan Failure-Mode Signatures
*Compiled project reference for the C-MAPSS fleet. FD001 engines
degrade via HPC (High-Pressure Compressor) efficiency loss.*

## §1 HPC degradation (primary FD001 mode)
Signature: **s_3 up** (HPC outlet temp), **s_7 down** and **s_11 down**
(HPC outlet pressures), **s_9 and s_14 up** (core speeds compensating),
**s_12 up** (fuel flow ratio), **s_4 up** (downstream LPT temp).
Physical cause: blade-tip clearance growth, erosion and fouling reduce
compressor efficiency; the core spools up and burns more fuel to hold
thrust, raising gas-path temperatures.
Risk at end of life: HPC surge/stall margin erosion, downstream
turbine overtemperature.

## §2 Fan-section degradation
Signature: **s_8 and s_13 drift** (fan speeds), **s_15 shift**
(bypass ratio), with core parameters comparatively stable early on.
Physical cause: fan blade erosion/FOD, leading-edge wear.

## §3 Healthy engine
All monitored sensors within ~2 baseline standard deviations, no
sustained monotone drift. No maintenance action indicated; continue
routine condition monitoring.

## §4 Ambiguity rule
If drift is present but weak (<2σ) or non-monotone, classify as
EARLY/UNCERTAIN degradation and recommend increased monitoring
frequency rather than immediate intervention.
