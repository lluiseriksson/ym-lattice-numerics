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
