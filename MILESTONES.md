# Milestones

`ym-lattice-numerics` is the empirical and numerical-certification anchor. It is Python/Julia-side
infrastructure and is exempt from the Lean toolchain lock.

## M0

Monte Carlo SU(2) in 4D, Wilson action, heat-bath + overrelaxation; mean plaquette vs beta against
strong- and weak-coupling expansions. Seeds are versioned.

## M1

Wilson loops and Creutz ratios, yielding string tension vs beta.

## M2

Temporal correlators of 0++ operators, yielding effective mass estimates for the lattice gap.

## M3

Interval arithmetic certifying the mother repository's explicit constant windows, for example
`(16d+1)^2 sigma < 1`, synchronized in `CONSTANTS.md` with the mother commit hash.

## M4

Honesty gap report: does the formal KP window fall where the physical gap is visible? The expected
answer is no; quantifying this gap is the deliverable.
