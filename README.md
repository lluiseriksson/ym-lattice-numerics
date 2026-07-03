# ym-lattice-numerics

Empirical anchoring and numerical-certification sidecar for the Yang-Mills lattice programme.

This repository is not a proof of the Yang-Mills mass gap. It exports reproducible datasets,
figures, and interval-arithmetic checks for explicit constants that may be consumed by the Lean
repositories. It exports no Lean theorem as established mathematics.

## Current scope

- M0 scaffold: 4D SU(2) Wilson-action Monte Carlo with heat-bath and overrelaxation sweeps.
- M1 scaffold: Wilson loops and Creutz-ratio helpers.
- M3 scaffold: interval-arithmetic checks for inequalities such as `(16d+1)^2 sigma < 1`.
- M2 and M4 are documented milestones, not completed deliverables.

The included Monte Carlo configuration is a smoke run, not a physics-grade ensemble.

## Reproducible commands

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev,plot]"
.venv\Scripts\python -m pytest
.venv\Scripts\python scripts\regenerate_all.py --config configs\m0_su2_smoke.yml
.venv\Scripts\python scripts\check_constants.py configs\constants_smoke.yml
```

Outputs are written under `data/` and `figures/`. Seeds and run parameters are stored in `configs/`.

## Synchronization pins

At repository creation, the mother repository `lluiseriksson/THE-ERIKSSON-PROGRAMME` had:

- main commit: `7a71754b93da6f447544211af51fd513a90b086c`
- Lean toolchain: `leanprover/lean4:v4.29.0-rc6`
- Mathlib commit: `07642720480157414db592fa85b626dafb71355b`

Those pins are recorded in `CONSTANTS.md` and `MATHLIB_AUDIT.md`. If the mother repository moves,
regenerate this metadata before treating any numerical window as synchronized.

## Honesty rules

- No hidden axioms, no implicit physical conclusions.
- Numerical evidence is labeled as numerical evidence.
- Placeholder constants are marked as smoke/example values.
- The expected M4 conclusion is that the formal KP window is far from the continuum-visible mass-gap
  regime; quantifying that gap is a deliverable, not something assumed here.
