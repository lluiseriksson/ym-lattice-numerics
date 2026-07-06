# Constants

This file is the human-readable synchronization surface for M3.

## Mother repository synchronization

- repository: `https://github.com/lluiseriksson/THE-ERIKSSON-PROGRAMME`
- synchronized branch: `main`
- synchronized commit: `42b77fae7118e6be69210233bfc7172bf7845eec`
- Lean toolchain: `leanprover/lean4:v4.29.0-rc6`
- Mathlib commit: `07642720480157414db592fa85b626dafb71355b`
- sidecar snapshot: `data/processed/mother_sync_snapshot.json`

## Certified windows

No theorem-relevant constant window has been imported yet.

The file `configs/constants_smoke.yml` is an executable schema example only. Its successful check is
not a mathematical claim about the programme.

## Required before claiming M3

- Import the real constants from the mother repository at a named commit.
- Store each value as an interval with explicit provenance.
- Run `python scripts/check_constants.py <constants-file>`.
- Commit the generated JSON report under `data/processed/`.
- Update this file with the report hash and pass/fail/unknown status.
