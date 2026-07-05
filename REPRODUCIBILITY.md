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
