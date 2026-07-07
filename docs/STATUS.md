# Hourly status heartbeat

Last audited by the hourly satellite: 2026-07-07T02:17:18+02:00.

## Repository state

- Default branch: `main`.
- Audited main HEAD: `8552c68d65ed2db1b790d57da4ec469b2386f12a`.
- Latest audited workflow runs on that HEAD:
  - `ci`: success, run `28830581467`
  - `heartbeat`: success, run `28830581450`
- Open PRs at audit time before this branch: none.
- Open issues with `agent-task`, `blocked`, or `interface-change`: `agent-task`
  #7, #34, and #42.

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
- `data/processed/mother_sync_snapshot.json`: metadata-only synchronization
  snapshot pinning the audited sidecar `main` and mother `main` without any
  mathematical claim.
- `scripts/aqft_bridges/gaussian_covariance_oracle.py` and
  `scripts/aqft_bridges/transfer_gap_oracle.py`: importable deterministic
  builders for the committed AQFT bridge certificate JSON files.
- `data/processed/witten_2602_0032_diagnostics.json`: conditional 2602.0032
  SU(2) `2^3` Hessian and Born-Oppenheimer `V_BO` proof-vs-literal
  diagnostics plus a synthetic finite-window transfer-matrix check, with exact
  file/API names for mother-side review.
- `data/processed/verify_2602_0041_report.json`: conditional 2602.0041
  Ricci, corrected beta-flow, geometric-sum, H-DOB kappa-window, and compact
  four-rotor entropy-pipeline plus Rothaus alpha bookkeeping contract for
  issue #42.
- `docs/DATASETS.md`: raw Monte Carlo JSON schema for smoke data.

## Current blockers for stronger claims

- No Lean theorem is exported by this repository.
- Mother synchronization pins reference mother main
  `48e066040c224c848d2f1f8b39d346de72d6506c`; the snapshot sidecar
  `audited_head` is the merged synchronization-pins commit.
- The certified honesty-gap report is a 2D sandbox report, not a 4D continuum
  statement.
- No gradient-flow integration is present; `docs/LEAN_YM_FLOW_COORDINATION.md`
  records the expected future interface.

## Next exact step

After the manifest round-trip check for `verify_2602_0041_lsi_h_dob` lands,
prefer a new exact `agent-task` sidecar artifact target. Do not extend issue
#34 again unless a specific upstream verifier/source reference is named.
