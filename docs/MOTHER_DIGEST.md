# Mother-facing digest

This digest records the small, safe surfaces that `THE-ERIKSSON-PROGRAMME`
could inspect or consume from this sidecar. It is not a proof artifact and it
exports no Lean theorem.

## Synchronization

- Last audited main HEAD for this digest:
  `c19fac9dc7f1e33302d3fefc8af1fa6b5dba1370`.
- Mother pins recorded in `CONSTANTS.md` and `MATHLIB_AUDIT.md`:
  - mother main commit: `7a71754b93da6f447544211af51fd513a90b086c`
  - Lean image: `leanprover/lean4:v4.29.0-rc6`
  - Mathlib commit: `07642720480157414db592fa85b626dafb71355b`
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
- `honesty_gap_2d`: `data/processed/honesty_gap_2d.json`
- `aqft_gaussian_covariance`:
  `data/processed/aqft_bridges/gaussian_covariance_certificate.json`,
  `data/processed/aqft_bridges/run_gaussian_covariance.log`
- `aqft_transfer_gap`:
  `data/processed/aqft_bridges/transfer_gap_certificate.json`,
  `data/processed/aqft_bridges/run_transfer_gap.log`

Manifest scope semantics:

- `m0_su2_smoke`: `smoke Monte Carlo dataset and plot`.
- `constants_smoke_report`: `synthetic constant-check schema example`.
- `honesty_gap_2d`: `certified exact-2D honesty-gap sidecar report`.
- `aqft_gaussian_covariance`: `finite-lattice Gaussian covariance numerical bridge oracle`.
- `aqft_transfer_gap`: `discrete Gaussian transfer-gap numerical bridge oracle`.

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
