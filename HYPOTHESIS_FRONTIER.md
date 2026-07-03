# Hypothesis Frontier

This is the exact frontier at repository creation.

## Lean status

- This repository exports no Lean lemmas.
- `Interfaces.lean` is intentionally empty except for a module comment.
- There are no Lean `sorry`s here because there is no Lean proof development in this repo.
- Toolchain lock status: `ym-lattice-numerics` is explicitly exempt from the Lean toolchain lock in
  the ecosystem prompt; the heartbeat therefore reports `toolchain_ok: true` and runs the Python
  test suite instead of `lake build`.

## Numerical frontier

- M0 currently provides a small reference SU(2) Monte Carlo kernel and smoke configuration.
- The smoke dataset is not a continuum extrapolation, not a production ensemble, and not evidence for
  a mass gap by itself.
- The heat-bath sampler is exact for the one-link SU(2) conditional distribution, but the present
  Python implementation is a reference implementation, not an optimized production kernel.
- Autocorrelation analysis, jackknife/bootstrap errors, finite-volume scans, and thermalization
  diagnostics are still frontier tasks.

## Constant-certification frontier

- `configs/constants_smoke.yml` contains example interval data only.
- No authoritative KP/Balaban window from the mother repository has been imported yet.
- `CONSTANTS.md` therefore does not certify any real theorem-relevant constant window today.

## Distance to programme objective

The repository currently establishes reproducible plumbing and basic invariants. It does not yet
quantify whether the formal KP window overlaps the physically visible mass-gap regime. The expected
scientific answer remains negative until measured and documented with synchronized constants.


## Second iteration (2026-07-03, push/m0-exact2d-certified) — closed

- `exact2d.py`: CERTIFIED interval enclosures (outward-rounded decimal, explicit
  geometric tail bounds) of the modified Bessel functions, the exact 2D mean
  plaquette `I_2(beta)/I_1(beta)`, and the exact 2D string tension
  `sigma = -log(I_2/I_1)`. This is the numerical twin of the
  `lean-2d-yang-mills` satellite.
- Cross-validation: the T0 heat-bath kernel reproduces the exact 2D plaquette
  at `beta = 1` within statistical errors (`tests/test_mc_vs_exact2d.py`).
- `analysis.py`: jackknife errors (exact on the mean), binning, Creutz-ratio
  string tension with errors (M1 estimator, exactly validated on a synthetic
  area law), effective masses (M2 estimator, exact on pure exponentials).
- `Interval.ln` added to the interval kernel (outward-rounded).
- M4 seed delivered: `scripts/honesty_gap_2d.py` +
  `data/processed/honesty_gap_2d.json`. With the certified exact 2D sigma, the
  formal window `(16d+1)^2 sigma < 1` at `d = 2` CERTIFIABLY FAILS at
  beta = 1, 2, 4 (physical couplings) and CERTIFIABLY PASSES at beta = 2000
  (sigma ~ 3/(2 beta)): the window opens three orders of magnitude in beta away
  from the physical region. This quantifies, with certificates on both sides,
  exactly the gap M4 was created to measure — in the 2D stand-in; the 4D
  version remains open.

## Still open

- M0 physics-grade 4D ensembles (current runs remain smoke-scale).
- M1 at physical couplings with autocorrelation-aware errors on real ensembles.
- M2 correlator measurements (the estimator exists; the 0++ operator
  measurement code does not yet).
- M3 against ACTUAL mother-repository constants synchronized by commit hash
  (the machinery is exercised; the real constants import is pending).
- M4 in 4D (the 2D certified stand-in above is the template).
