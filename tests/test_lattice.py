from __future__ import annotations

import numpy as np

from ym_lattice_numerics.lattice import LatticeSpec, cold_start, heatbath_sweep, mean_plaquette, overrelaxation_sweep
from ym_lattice_numerics.observables import creutz_ratio_from_links, mean_wilson_loop


def test_cold_start_observables_are_trivial() -> None:
    links = cold_start(LatticeSpec(length=2, ndim=4))
    assert mean_plaquette(links) == 1.0
    assert mean_wilson_loop(links, 1, 1) == 1.0
    assert creutz_ratio_from_links(links, 2, 2) == -0.0


def test_update_sweeps_preserve_unit_links() -> None:
    rng = np.random.default_rng(789)
    links = cold_start(LatticeSpec(length=2, ndim=4))
    heatbath_sweep(links, beta=0.5, rng=rng)
    overrelaxation_sweep(links)
    norms = np.linalg.norm(links, axis=-1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-12)
