# Reproducibility

Every generated artifact must be recoverable from a versioned config and a command.

## Smoke regeneration

```powershell
python scripts\regenerate_all.py --config configs\m0_su2_smoke.yml
```

This writes:

- `data/raw/m0_su2_smoke.json`
- `data/raw/m0_su2_smoke.csv`
- `figures/m0_su2_smoke_plaquette.png`

## Constant checks

```powershell
python scripts\check_constants.py configs\constants_smoke.yml
```

This writes:

- `data/processed/constants_smoke_report.json`

The smoke constants are schema examples only.

## Certified 2D honesty-gap report

```powershell
python scripts\honesty_gap_2d.py --output data\processed\honesty_gap_2d.json
```

This writes:

- `data/processed/honesty_gap_2d.json`

This command is intentionally separate from `scripts/regenerate_all.py`: it
regenerates a deterministic certified 2D sidecar report, while
`regenerate_all.py` is the smoke Monte Carlo and plot refresh entrypoint.

## AQFT bridge certificates

```powershell
python scripts\aqft_bridges\gaussian_covariance_oracle.py --output data\processed\aqft_bridges\gaussian_covariance_certificate.json
python scripts\aqft_bridges\transfer_gap_oracle.py --output data\processed\aqft_bridges\transfer_gap_certificate.json
```

These write:

- `data/processed/aqft_bridges/gaussian_covariance_certificate.json`
- `data/processed/aqft_bridges/transfer_gap_certificate.json`

The paired `run_*.log` files are audit logs committed with the manifest outputs;
temporary round-trip tests redirect only the certificate JSON path.

Committed audit-log outputs:

- `data/processed/aqft_bridges/run_gaussian_covariance.log`
- `data/processed/aqft_bridges/run_transfer_gap.log`

## Conditional 2602.0032 Witten-lattice diagnostics

```powershell
python scripts\witten_2602_0032_diagnostics.py --output data\processed\witten_2602_0032_diagnostics.json
```

This writes:

- `data/processed/witten_2602_0032_diagnostics.json`

The report records only finite-dimensional numerical diagnostics for the
conditional 2602.0032 paper: the SU(2) `2^3` Wilson-action Hessian at
`theta = 0`, a generic-theta Hessian check, a quartic toron ratio, and the
Born-Oppenheimer `V_BO` proof-formula versus literal-formula diagnostic from
the reference verification script. It is not a proof artifact or a continuum
claim.

## Conditional 2602.0041 LSI/H-DOB window contract

```powershell
python scripts\verify_2602_0041.py --output data\processed\verify_2602_0041_report.json
```

This writes:

- `data/processed/verify_2602_0041_report.json`

The report records a deterministic verifier-boundary subset for the 2602.0041
package: Ricci convention coherence for `Ric = Nc/2` at `SU(2)`, the corrected
decreasing beta flow, the elementary geometric sum `r/(1-r)^2`, and an explicit
H-DOB kappa-vs-beta window exhibit. It also records a finite compact
four-rotor entropy pipeline on an 8-point grid as a deterministic conditional
diagnostic. It does not discharge H-XSD or H-DOB and is not a
source-construction, hRpoly, continuum, mass-gap, or Clay claim.
