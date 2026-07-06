# Hourly status heartbeat

Last audited by the hourly satellite: 2026-07-06T10:10:40+02:00.

## Repository state

- Default branch: `main`.
- Audited main HEAD: `ab511c830ec666e1e28f10de9993acb687f67db1`.
- Latest audited workflow runs on that HEAD:
  - `ci`: success, run `28775071727`
  - `heartbeat`: success, run `28775071730`
- Open PRs at audit time before this branch: none.
- Open issues with `agent-task`, `blocked`, or `interface-change`: `agent-task`
  #7 and #34.

## Mother-facing surfaces currently worth consuming

- `docs/MOTHER_DIGEST.md`: exact API/file/hypothesis digest for sidecar
  consumption limits.
- `src/ym_lattice_numerics/exact2d.py`: certified exact 2D SU(2) interval
  helpers for the sandbox layer.
- `src/ym_lattice_numerics/intervals.py`: outward-rounded interval arithmetic
  and trivalent inequality checks.
- `data/processed/honesty_gap_2d.json`: schema-versioned 2D honesty-gap seed
  for `(16*d+1)^2*sigma < 1`.
- `data/processed/artifact_manifest.json`: machine-readable map from generated
  sidecar artifacts to exact regeneration commands, inputs, outputs, and
  verification commands.
- `scripts/aqft_bridges/gaussian_covariance_oracle.py` and
  `scripts/aqft_bridges/transfer_gap_oracle.py`: importable deterministic
  builders for the committed AQFT bridge certificate JSON files.
- `data/processed/witten_2602_0032_diagnostics.json`: conditional 2602.0032
  SU(2) `2^3` Hessian and Born-Oppenheimer `V_BO` proof-vs-literal
  diagnostics with exact file/API names for mother-side review.
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

After the conditional 2602.0032 Born-Oppenheimer diagnostic lands, extend the
same JSON pattern to the finite-window doubling diagnostic only if it can
remain small, deterministic, and clearly conditional.
