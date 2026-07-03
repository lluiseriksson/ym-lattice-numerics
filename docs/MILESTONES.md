# Milestones

## M0: SU(2) Wilson Monte Carlo

Status: scaffold implemented.

- Heat-bath and overrelaxation sweeps exist as a Python reference kernel.
- Mean plaquette is measured.
- Smoke datasets regenerate from `configs/m0_su2_smoke.yml`.
- Production validation against strong/weak coupling expansions remains open.

## M1: Wilson loops and Creutz ratios

Status: helper functions implemented, production analysis open.

- Rectangular Wilson loops and Creutz ratios are available.
- Error analysis and beta scans are not yet complete.

## M2: 0++ correlators and effective mass

Status: not implemented.

- Operator basis, smearing, temporal correlators, covariance handling, and effective-mass plots are
  frontier tasks.
- Gradient-flow smearing and scale setting should coordinate with `lean-ym-flow`; see
  `docs/LEAN_YM_FLOW_COORDINATION.md`.

## M3: Interval-certified constants

Status: executable schema implemented.

- `(16d+1)^2 sigma < 1` can be checked with outward-rounded decimal intervals.
- Only smoke constants are present.
- Real constants must be imported from a named mother-repo commit before any certificate is claimed.

## M4: Honesty report

Status: not implemented.

The deliverable is a quantitative comparison between the formal KP window and the physics-visible
mass-gap regime. The expected answer is no overlap; this repo must measure and document the gap.
