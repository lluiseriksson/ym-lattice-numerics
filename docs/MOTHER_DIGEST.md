# Mother-facing digest

This digest records the small, safe surfaces that `THE-ERIKSSON-PROGRAMME`
could inspect or consume from this sidecar. It is not a proof artifact and it
exports no Lean theorem.

## Synchronization

- Last audited main HEAD for this digest:
  `814820004d0b363791561bcc1cf1721a831e04d7`.
- Mother pins recorded in `CONSTANTS.md` and `MATHLIB_AUDIT.md`:
  - mother main commit: `7e08458bcce48a9080a21fe90375cae62557a122`
  - Lean image: `leanprover/lean4:v4.29.0-rc6`
  - Mathlib commit: `07642720480157414db592fa85b626dafb71355b`
- Machine-readable synchronization snapshot:
  `data/processed/mother_sync_snapshot.json`.
- Re-synchronize those files before treating any exported number as aligned
  with a newer mother commit.
- `docs/STATUS.md` records the latest hourly satellite heartbeat and the next
  exact sidecar step.
- `tests/test_mother_digest_contract.py` checks that documented Python API
  names still exist in the modules named by this digest.

## Exact 2D certified layer

File: `src/ym_lattice_numerics/exact2d.py`

Exported Python APIs:

- `bessel_i_interval(nu, beta, terms=40) -> Interval`
- `plaquette_exact_interval(beta, terms=40) -> Interval`
- `string_tension_exact_interval(beta, terms=40) -> Interval`
- Float midpoint helpers: `bessel_i`, `plaquette_exact`,
  `string_tension_exact`, `strong_coupling_plaquette`

Hypotheses and scope:

- Two-dimensional SU(2) Wilson action only.
- `beta > 0` for plaquette and string-tension helpers.
- Bessel enclosures use the modified-Bessel power series plus an explicit
  geometric tail bound; if `terms` is too small, the code raises `ValueError`.
- The string tension is the exact infinite-volume 2D value
  `sigma(beta) = -log(I_2(beta) / I_1(beta))`.
- The finite-volume note in the module docstring is descriptive context for
  the test sizes, not a Lean-ready theorem exported by this repository.

Possible mother consumption:

- Treat interval endpoints as an empirical/certified sidecar datum for the
  exactly soluble 2D sandbox.
- Do not use this as evidence for four-dimensional continuum Yang-Mills or as
  a mass-gap claim.

## Mother synchronization snapshot

Files:

- Producer: `scripts/mother_sync_snapshot.py`
- Config: `configs/mother_sync_snapshot.yml`
- Output: `data/processed/mother_sync_snapshot.json`
- Test: `tests/test_mother_sync_snapshot.py`

Payload fields:

- `schema_version`
- `audited_at`
- `honesty`
- `sidecar`
- `mother`
- `observed_by`
- `notes`

Current pins:

- Sidecar audited by the committed snapshot:
  `814820004d0b363791561bcc1cf1721a831e04d7`.
- Mother `main`: `7e08458bcce48a9080a21fe90375cae62557a122`.
- Lean image: `leanprover/lean4:v4.29.0-rc6`.
- Mathlib commit: `07642720480157414db592fa85b626dafb71355b`.

Possible mother consumption:

- Use this JSON as the metadata-only synchronization surface before checking
  whether sidecar constants are aligned with the mother repository.
- Treat it as routing metadata only; it is not a Lean theorem, continuum
  statement, source construction, or mass-gap claim.
- Refresh this snapshot before using it for any sidecar state after
  `814820004d0b363791561bcc1cf1721a831e04d7`.

## Interval arithmetic surface

File: `src/ym_lattice_numerics/intervals.py`

Exported Python APIs:

- `Interval(lo, hi)`
- `Interval.point(value)`
- `Interval.parse(value)`
- arithmetic: `+`, `-`, `*`, `/`, `reciprocal()`, `pow_int(exponent)`,
  `ln()`
- `sum_intervals(values)`
- `certify_less(lhs, rhs) -> "pass" | "fail" | "unknown"`

Hypotheses and scope:

- Decimal precision is fixed by `PRECISION = 80`.
- Elementary operations use outward-directed decimal rounding.
- `ln()` requires a strictly positive interval.
- `certify_less` is a trivalent interval comparison and should be treated as
  inconclusive when it returns `unknown`.

Possible mother consumption:

- Use the JSON strings produced by `Interval.to_json()` as exact decimal input
  for independent checking.
- Re-check any critical inequality in Lean or another trusted checker before
  promoting it to a formal statement.

## M4 honesty-gap seed

Files:

- Producer: `scripts/honesty_gap_2d.py`
- Output: `data/processed/honesty_gap_2d.json`

Exact expression:

- `(16*d+1)^2*sigma < 1`
- evaluated at `d = 2`
- with `sigma = -log(I_2(beta)/I_1(beta))` from the certified exact 2D layer

JSON schema version:

- `schema_version: 1`

Payload fields:

- `expression`
- `honesty`
- `results[]`
- per result: `beta`, `regime`, `sigma_exact_2d`,
  `window_lhs_(16d+1)^2*sigma`, `certification_lhs_lt_1`

Current certified statuses:

- `beta = 1`: `fail`
- `beta = 2`: `fail`
- `beta = 4`: `fail`
- `beta = 2000`: `pass`

Hypotheses and scope:

- This is an exact 2D stand-in for an explicit formal window, not the 4D
  quantity the mother ultimately cares about.
- The JSON quantifies where this formal inequality opens in the 2D sandbox.
- It must not be cited as a continuum, source-construction, or mass-gap result.

Possible mother consumption:

- Import the schema as a sidecar report for the M4 honesty-gap narrative.
- Point a future checker at `sigma_exact_2d` and
  `window_lhs_(16d+1)^2*sigma` endpoints to reproduce each `pass` or `fail`.

## Statistical estimator layer

File: `src/ym_lattice_numerics/analysis.py`

Exported Python APIs:

- `jackknife(values, estimator=None)`
- `binned_series(values, bin_size)`
- `binned_error(values, bin_size)`
- `creutz_string_tension(w11, w12, w22)`
- `effective_mass(correlator)`

Hypotheses and scope:

- These are numerical estimators tested on deterministic synthetic cases.
- They do not measure production-grade ensembles by themselves.
- `effective_mass` requires positive correlator entries.
- `creutz_string_tension` assumes paired Wilson-loop samples with matching
  lengths.

Possible mother consumption:

- Use only as reproducible analysis infrastructure for future sidecar datasets.
- Do not treat estimator existence as evidence that M1 or M2 physics deliverables
  are complete.

## AQFT bridge oracles

Files:

- `scripts/aqft_bridges/gaussian_covariance_oracle.py`
- `scripts/aqft_bridges/transfer_gap_oracle.py`
- `data/processed/aqft_bridges/gaussian_covariance_certificate.json`
- `data/processed/aqft_bridges/transfer_gap_certificate.json`
- `data/processed/aqft_bridges/run_gaussian_covariance.log`
- `data/processed/aqft_bridges/run_transfer_gap.log`

Payloads:

- `gaussian_covariance_certificate.json` records finite-lattice massive
  Gaussian covariance checks for 1D chains and a 2D grid: coercivity proxy `c`,
  Schur bound `S`, admissible Combes-Thomas-style rate `theta_adm`, fitted 1D
  sharp rates, and mass-to-zero guardrails.
- `transfer_gap_certificate.json` records a discrete Gaussian transfer-matrix
  sanity oracle: transfer gap, covariance clustering rate, and
  `arccosh(1 + m^2/2)` agree numerically for the tested masses, with small-mass
  guardrails.

Importable script APIs:

- `gaussian_covariance_oracle.build_certificate()`
- `gaussian_covariance_oracle.write_certificate(cert, output)`
- `gaussian_covariance_oracle.main(argv=None)`
- `transfer_gap_oracle.build_certificate()`
- `transfer_gap_oracle.write_certificate(cert, output)`
- `transfer_gap_oracle.main(argv=None)`

Possible mother/satellite consumption:

- Treat these as numerical acceptance oracles for future
  `lean-gaussian-field` and `lean-transfer-matrix` M3 work.
- Import `build_certificate()` in tests or satellite checks to compare the
  committed JSON certificates with deterministic rebuilds.
- For manifest-driven CLI checks, run each AQFT artifact `command_argv` with
  its `--output` argument redirected to a temporary certificate path, then
  compare the generated JSON with the corresponding `build_certificate()`
  payload.
- Use them as sidecar data only; they are not Lean theorems and do not prove
  a Yang-Mills activity estimate.
- The scripts are intentionally under `scripts/aqft_bridges/` to keep them
  separate from the SU(2) lattice Monte Carlo path.

## Conditional 2602.0032 Witten-lattice diagnostic

Files:

- Producer: `scripts/witten_2602_0032_diagnostics.py`
- Output: `data/processed/witten_2602_0032_diagnostics.json`
- Test: `tests/test_witten_2602_0032_diagnostics.py`

Importable script APIs:

- `witten_2602_0032_diagnostics.build_report()`
- `witten_2602_0032_diagnostics.write_report(report, output)`
- `witten_2602_0032_diagnostics.main(argv=None)`

Payload fields:

- `schema_version`
- `source`
- `honesty`
- `diagnostics.wilson_hessian_su2_2x2x2`
- `diagnostics.born_oppenheimer_vbo_lemma_5_2`
- `diagnostics.finite_window_transfer_matrix_synthetic`
- `theta_zero.kernel_dimension`
- `theta_zero.flat_tangent_dimension_reference`
- `theta_zero.max_abs_deviation_from_maxwell_reference`
- `theta_zero.nonzero_eigenvalues_unique`
- `quartic_toron_ratio.ratio`
- `generic_theta.kernel_dimension`
- `generic_theta.min_positive_eigenvalue`
- `hessian_rows[].proof_hessian_diag_over_S1`
- `hessian_rows[].literal_hessian_diag`
- `grid_scan.proof_min_off_coroot_lattice`
- `grid_scan.literal_min`
- `rows[].grid_size`
- `rows[].normalized_gap`
- `rows[].window_normalized_gap`
- `max_gap_change_after_doubling`

Current diagnostic values:

- SU(2) spatial lattice: `2^3`.
- Variables in the finite-difference Hessian: `72`.
- At `theta = 0`, kernel dimension: `30`.
- Reference flat-tangent dimension recorded for comparison: `24`.
- Nonzero Hessian eigenvalue representatives: `2.0`, `4.0`, `6.0`.
- Quartic toron ratio `S(2t)/S(t)` at `t = 0.02`: about `15.9936`.
- At generic `theta = [0.53, 0.91, 0.36]`, kernel dimension: `26`.
- Born-Oppenheimer `V_BO` proof-formula rows:
  - `SU(2), L=4`: `Hess_proof/S1 = 2.0`, literal Hessian diagonal
    about `-0.1167`.
  - `SU(2), L=8`: `Hess_proof/S1 = 2.0`, literal Hessian diagonal
    about `-0.0722`.
  - `SU(3), L=4`: `Hess_proof/S1 = 3.0`, literal Hessian diagonal
    about `-0.1750`.
- Born-Oppenheimer `SU(2), L=4` grid scan over `15^3` points:
  `proof_min_off_coroot_lattice` about `9.9158`, `literal_min` about
  `-2.4495` at `[-4.4429, -4.4429, -4.4429]`, using the first grid point
  under the explicit tie-break.
- Synthetic finite-window transfer-matrix check:
  one compact rotor with cosine coupling and cosine pinning, `beta = 0.85`,
  `pinning = 0.2`, and window `|theta| <= pi/2`.
- Transfer-matrix grid sizes: `8`, `16`, and `32`, with window point counts
  `5`, `9`, and `17`.
- Full-matrix normalized gap is about `0.615019` on the finer grids, with
  `max_gap_change_after_doubling = 5.05042e-07`.
- Window-restricted normalized gaps are about `0.615914`, `0.644968`, and
  `0.660913`.

Possible mother consumption:

- Use this JSON as a finite-dimensional diagnostic for issue #34's
  conditional 2602.0032 review surface.
- Treat `theta_zero.kernel_dimension`, `generic_theta.kernel_dimension`, and
  `quartic_toron_ratio.ratio` as reproducible numerical checks, not as
  theorem exports.
- Treat the Born-Oppenheimer rows as a finite-dimensional proof-formula versus
  literal-formula diagnostic only.
- Treat the finite-window transfer matrix as a synthetic sanity check only,
  not as a transfer operator construction for the conditional paper.
- The report is intentionally scoped to one diagnostic cluster from the
  reference `verify_2602_0032.py`; it does not assert any continuum
  reconstruction or physical gap.

## Conditional 2602.0041 LSI/H-DOB window contract

Files:

- Producer: `scripts/verify_2602_0041.py`
- Output: `data/processed/verify_2602_0041_report.json`
- Test: `tests/test_verify_2602_0041.py`

Importable script APIs:

- `verify_2602_0041.build_report()`
- `verify_2602_0041.write_report(report, output)`
- `verify_2602_0041.main(argv=None)`

Payload fields:

- `schema_version`
- `source`
- `honesty`
- `diagnostics.ricci_convention`
- `diagnostics.corrected_beta_flow`
- `diagnostics.geometric_sum`
- `diagnostics.h_dob_kappa_window_exhibit`
- `diagnostics.compact_four_rotor_entropy_pipeline`
- `diagnostics.rothaus_alpha_tradeoff`
- per beta-flow row: `beta`, `b0_su2`, `C_Nc_equals_1_over_2b0`,
  `step_2_b0_log2`, `n_max_estimate`, `n_floor`, `beta_at_n_floor`,
  `beta_at_n_floor_plus_1`, `floor_brackets_zero`
- per H-DOB row: `beta`, `n_floor_from_corrected_flow`, `log_R_nmax`,
  `C_Gamma_model`, `threshold_log_rhs`, `fixed_kappa_exhibit`,
  `fixed_kappa_exceeds_threshold`
- per Rothaus alpha row: `alpha`,
  `constant_multiplier_1_over_1_minus_alpha`,
  `defect_multiplier_1_over_alpha`, `toy_combined_cost`

Current diagnostic values:

- Ricci convention row: `SU(2)`, `Ric = Nc/2`, value `1.0`.
- Corrected beta flow: `beta_k = beta - 2*b0*k*log(2)` with beta grid
  `10.0`, `20.0`, `40.0`; each `n_floor` brackets the zero crossing.
- Geometric sum check: for `r = 0.5`, `r/(1-r)^2 = 2.0`.
- H-DOB exhibit shape:
  `kappa > log[((M R_nmax)^d C_Gamma r)/(1-r)^2]`.
- Exhibit parameters: `d = 4`, `M = 2.0`, `r = 0.5`,
  `C_Gamma = (n_floor + 1)^2`, fixed `kappa = 250.0`.
- The threshold increases on the beta grid; fixed kappa covers the first row
  but not the larger-beta rows in this exhibit.
- Compact four-rotor entropy pipeline: `rotor_count = 4`,
  `grid_points_per_rotor = 8`, `beta = 0.75`, `state_count = 4096`,
  with Gibbs weights from
  `sum_i (1 - cos(theta_{i+1} - theta_i))` on a discrete torus and the
  checked identity `D(mu||uniform) = log(state_count) - H(mu)`.
- Rothaus alpha tradeoff grid: `alpha = 0.125`, `0.25`, `0.5`, `0.75`,
  and `0.875`; toy formula
  `toy_cost(alpha) = C0/(1-alpha) + epsilon/alpha` with `C0 = 2.0` and
  `epsilon = 0.25`; grid minimizer `alpha = 0.25`. This is bookkeeping for
  constants and defects, not a formal Rothaus lemma.

Possible mother consumption:

- Use the JSON as a CI-backed contract for issue #42's verifier-boundary
  routing before importing a fuller 2602.0041 verifier.
- Treat the rows, finite entropy pipeline, and alpha grid as deterministic
  diagnostics of formulas and window pressure, not as a proof of H-XSD,
  H-DOB, companion papers 2602.0054-2602.0057, source construction, hRpoly,
  continuum construction, mass gap, or Clay.

## Sidecar artifact manifest

File: `data/processed/artifact_manifest.json`

Schema fields:

- `schema_version`
- `honesty`
- `artifacts[]`
- per artifact: `id`, `scope`, `producer`, `command_argv`, `inputs`,
  `outputs`, `verification`
- optional per artifact: `stdout_log`

Current artifact ids and outputs:

- `m0_su2_smoke`: `data/raw/m0_su2_smoke.json`,
  `data/raw/m0_su2_smoke.csv`, `figures/m0_su2_smoke_plaquette.png`
- `constants_smoke_report`: `data/processed/constants_smoke_report.json`
- `mother_sync_snapshot`: `data/processed/mother_sync_snapshot.json`
- `honesty_gap_2d`: `data/processed/honesty_gap_2d.json`
- `aqft_gaussian_covariance`:
  `data/processed/aqft_bridges/gaussian_covariance_certificate.json`,
  `data/processed/aqft_bridges/run_gaussian_covariance.log`
- `aqft_transfer_gap`:
  `data/processed/aqft_bridges/transfer_gap_certificate.json`,
  `data/processed/aqft_bridges/run_transfer_gap.log`
- `witten_2602_0032_hessian`:
  `data/processed/witten_2602_0032_diagnostics.json`
- `verify_2602_0041_lsi_h_dob`:
  `data/processed/verify_2602_0041_report.json`

Manifest scope semantics:

- `m0_su2_smoke`: `smoke Monte Carlo dataset and plot`.
- `constants_smoke_report`: `synthetic constant-check schema example`.
- `mother_sync_snapshot`: `metadata-only mother synchronization snapshot`.
- `honesty_gap_2d`: `certified exact-2D honesty-gap sidecar report`.
- `aqft_gaussian_covariance`: `finite-lattice Gaussian covariance numerical bridge oracle`.
- `aqft_transfer_gap`: `discrete Gaussian transfer-gap numerical bridge oracle`.
- `witten_2602_0032_hessian`: `conditional 2602.0032 SU(2) 2^3 Hessian diagnostic`.
- `verify_2602_0041_lsi_h_dob`: `conditional 2602.0041 LSI/H-DOB window verifier contract`.

AQFT manifest contract:

- `aqft_gaussian_covariance` uses producer
  `scripts/aqft_bridges/gaussian_covariance_oracle.py` and
  `command_argv` beginning with
  `python scripts/aqft_bridges/gaussian_covariance_oracle.py --output`.
- `aqft_transfer_gap` uses producer
  `scripts/aqft_bridges/transfer_gap_oracle.py` and `command_argv` beginning
  with `python scripts/aqft_bridges/transfer_gap_oracle.py --output`.
- In round-trip checks, the declared certificate output path may be replaced
  by a temporary certificate path; the committed `stdout_log` entries are
  audit-only outputs and are not rewritten by that temporary run.
- The generated temporary certificate JSON should match the corresponding
  `build_certificate()` payload, allowing only the repository test tolerance
  for floating-point last-bit drift.
- Each committed `stdout_log` must end with a `certificate written:` line whose
  path matches the certificate output declared by the manifest `command_argv`.

M0 smoke manifest contract:

- `scripts/regenerate_all.py` keeps the manifest `command_argv` default paths
  for committed refreshes.
- For round-trip checks, callers may pass `--output-json`, `--output-csv`, and
  `--output-figure` to redirect all generated M0 smoke outputs to temporary
  paths before comparing deterministic JSON/CSV payloads and checking the PNG
  render shape against the committed figure.

Conditional 2602.0032 manifest contract:

- `witten_2602_0032_hessian` uses producer
  `scripts/witten_2602_0032_diagnostics.py` and `command_argv` beginning with
  `python scripts/witten_2602_0032_diagnostics.py --output`.
- `tests/test_witten_2602_0032_diagnostics.py` compares the committed JSON
  with `build_report()` and checks the expected kernel dimensions, eigenvalue
  representatives, generic-theta positivity, quartic toron ratio, and the
  Born-Oppenheimer proof-formula versus literal-formula rows.
- The same test file checks the synthetic transfer-matrix grid sizes,
  window point counts, symmetry error, normalized gaps, and gap stability
  under grid doubling.
- The diagnostic is conditional paper evidence only; it is not a Lean theorem,
  a source construction, a continuum statement, or a mass-gap claim.

Conditional 2602.0041 manifest contract:

- `verify_2602_0041_lsi_h_dob` uses producer
  `scripts/verify_2602_0041.py` and `command_argv` beginning with
  `python scripts/verify_2602_0041.py --output`.
- `tests/test_verify_2602_0041.py` compares the committed JSON with
  `build_report()` and checks the Ricci convention row, corrected beta-flow
  zero bracketing, geometric sum, monotone H-DOB kappa-window exhibit, compact
  four-rotor entropy-pipeline identity, and Rothaus alpha tradeoff grid.
- The contract is formula-routing evidence only; it does not discharge H-XSD
  or H-DOB and does not prove source construction, hRpoly, continuum
  construction, a mass gap, or Clay.

Possible mother/satellite consumption:

- Use `command_argv` as the exact local regeneration command for each listed
  sidecar artifact.
- Use `producer`, `inputs`, `outputs`, and `verification` to decide whether a
  PR has updated generated files and their check surface together.
- Treat the manifest as reproducibility routing only; it is not a proof
  artifact or a mathematical claim.

## Current blockers for stronger consumption

- No Lean import surface exists in this repository; `INTERFACES.md` explicitly
  says this repo exports data, not Lean theorems.
- Mother synchronization is pinned to the commits above and must be refreshed
  before any new cross-repo claim.
- The M4 report is 2D-only; a 4D constant-window comparison needs a separate
  source for the relevant four-dimensional quantity and uncertainty model.
