# Hourly status heartbeat

Last audited by the hourly satellite: 2026-07-04T17:18:47+02:00.

## Repository state

- Default branch: `main`.
- Audited main HEAD: `210b7dfd589aa9e74b024827835d650c19562d9c`.
- Latest audited workflow runs on that HEAD:
  - `ci`: success, run `28709061357`
  - `heartbeat`: success, run `28709061353`
- Open PRs at audit time: none.
- Open issues with `agent-task`, `blocked`, or `interface-change`: `agent-task`
  #7.

## Mother-facing surfaces currently worth consuming

- `docs/MOTHER_DIGEST.md`: exact API/file/hypothesis digest for sidecar
  consumption limits.
- `src/ym_lattice_numerics/exact2d.py`: certified exact 2D SU(2) interval
  helpers for the sandbox layer.
- `src/ym_lattice_numerics/intervals.py`: outward-rounded interval arithmetic
  and trivalent inequality checks.
- `data/processed/honesty_gap_2d.json`: schema-versioned 2D honesty-gap seed
  for `(16*d+1)^2*sigma < 1`.
- `docs/DATASETS.md`: raw Monte Carlo JSON schema for smoke data.

## Current blockers for stronger claims

- No Lean theorem is exported by this repository.
- Mother synchronization pins still reference the commits recorded in
  `CONSTANTS.md` and `MATHLIB_AUDIT.md`; refresh them before cross-repo claims.
- The certified honesty-gap report is a 2D sandbox report, not a 4D continuum
  statement.
- No gradient-flow integration is present; `docs/LEAN_YM_FLOW_COORDINATION.md`
  records the expected future interface.

## Next exact step

If another processed sidecar report is added, create a machine-readable
artifact manifest mapping each generated file to its exact regeneration
command. Keep `scripts/regenerate_all.py` scoped to smoke Monte Carlo and plot
refreshes until such a manifest exists.
