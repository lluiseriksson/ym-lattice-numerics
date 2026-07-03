# Interfaces

This repository exports data, not Lean theorems.

Stable exported surfaces:

- `CONSTANTS.md`: human-readable synchronization record for explicit constant windows.
- `data/raw/*.json`: raw reproducible Monte Carlo runs with full configuration metadata.
- `data/processed/*.json`: processed constant-check or observable summaries.
- `figures/*`: regenerated figures, never hand-edited.

Breaking changes:

- Renaming any top-level key in raw run JSON.
- Renaming constant-check result fields.
- Changing the meaning of `plaquette_mean`, Wilson-loop normalization, or Creutz-ratio convention.

No downstream Lean repository should import a theorem from this repo. If a future Lean sidecar is
added, its signatures must be documented here before use.
