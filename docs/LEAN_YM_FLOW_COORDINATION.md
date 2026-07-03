# Coordination with lean-ym-flow

This repository should use gradient flow outputs from `lean-ym-flow` when that sidecar exists.

Expected integration points:

- Use flowed gauge fields as smearing inputs for Wilson loops and 0++ operator construction.
- Record the flow action density convention before deriving `t0`.
- Store `t0/a^2` estimates in processed datasets with the same seed/config provenance as raw runs.
- Add a scale-setting block to `CONSTANTS.md` only after the mother commit and flow commit are both
  pinned.

No gradient-flow implementation is present in this repository today.
