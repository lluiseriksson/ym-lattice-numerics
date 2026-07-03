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
