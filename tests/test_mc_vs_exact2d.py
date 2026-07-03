from __future__ import annotations

import numpy as np

from ym_lattice_numerics.exact2d import plaquette_exact
from ym_lattice_numerics.lattice import LatticeSpec, heatbath_sweep, hot_start, mean_plaquette


def test_mc_2d_matches_exact_bessel_ratio() -> None:
    """Cross-validation of the heat-bath kernel against the exactly soluble
    2D theory: the numerical twin of the lean-2d-yang-mills sandbox."""

    beta = 1.0
    spec = LatticeSpec(length=8, ndim=2)
    rng = np.random.default_rng(20260703)
    links = hot_start(spec, rng)

    for _ in range(40):
        heatbath_sweep(links, beta, rng)

    samples = []
    for _ in range(60):
        heatbath_sweep(links, beta, rng)
        samples.append(mean_plaquette(links))

    mc = float(np.mean(samples))
    exact = plaquette_exact(beta)
    # 64 plaquettes x 60 measurements: statistical error well below 0.02.
    assert abs(mc - exact) < 0.02, (mc, exact)
