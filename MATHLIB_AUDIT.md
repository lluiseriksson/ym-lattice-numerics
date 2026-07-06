# Mathlib Audit

Audit date: 2026-07-06.

Mother repository pins observed:

- Mother main commit: `6ea7c8c0504c87b0e01ebdd4ae179ac53846717c`
- `lean-toolchain`: `leanprover/lean4:v4.29.0-rc6`
- Mathlib: `leanprover-community/mathlib4@07642720480157414db592fa85b626dafb71355b`
- Snapshot: `data/processed/mother_sync_snapshot.json`

Local audit method:

- Refreshed mother repository metadata from `main` on 2026-07-06.
- The Mathlib commit did not change from the previous audit.
- Checked out Mathlib at the pinned commit in `work/mathlib4-audit` during the original API audit.
- Searched relevant Lean files with `rg` for unitary groups, special unitary groups, Haar/probability
  infrastructure, and lattice Yang-Mills-specific terminology.

## Found in Mathlib

- `Mathlib.LinearAlgebra.UnitaryGroup` defines `Matrix.UnitaryGroup` and
  `Matrix.specialUnitaryGroup`.
- `Mathlib.LinearAlgebra.Matrix.SpecialLinearGroup` defines matrix special linear groups.
- Measure/probability infrastructure exists, including Haar-measure and probability-measure
  typeclasses, kernels, product measures, variance, and strong law material.
- Interval/order infrastructure exists for mathematical intervals, but this repo's M3 numerical
  interval arithmetic is implemented externally in Python and does not assert Lean theorems.

## Not found as reusable domain API

Searches did not find a Mathlib API for:

- Wilson lattice gauge action.
- Plaquettes or Wilson loops as lattice-gauge observables.
- Creutz ratios.
- Balaban/Kotecky-Preiss lattice Yang-Mills constants.
- A formal mass-gap assembly interface specific to this programme.

## Consequence

This repo should not duplicate general Mathlib material in Lean. It should export only:

- synchronized constant files,
- reproducible numerical datasets,
- figure-generation commands,
- interval-check reports.

Any future Lean-facing statement should first be proposed either upstream to Mathlib if general, or
to the mother Lean repository if programme-specific.
