from __future__ import annotations

import math

import numpy as np

from ym_lattice_numerics.analysis import (
    binned_error,
    binned_series,
    creutz_string_tension,
    effective_mass,
    jackknife,
)


def test_jackknife_mean_equals_standard_error() -> None:
    data = [1.0, 2.0, 3.0, 4.0]
    est, err = jackknife(data)
    assert est == 2.5
    expected = np.std(data, ddof=1) / math.sqrt(len(data))
    assert abs(err - expected) < 1e-12


def test_binned_series_shapes() -> None:
    bins = binned_series([1, 1, 3, 3, 5, 5, 7], 2)
    assert list(bins) == [1.0, 3.0, 5.0]
    assert binned_error([1, 1, 3, 3, 5, 5, 7], 2) > 0


def test_effective_mass_exact_on_exponential() -> None:
    m = 0.7
    corr = [5.0 * math.exp(-m * t) for t in range(6)]
    for value in effective_mass(corr):
        assert abs(value - m) < 1e-12


def test_creutz_string_tension_exact_area_law() -> None:
    # Exact area law W(RxT) = exp(-sigma R T): chi(2,2) recovers sigma.
    sigma = 0.3
    w = lambda r, t: math.exp(-sigma * r * t)
    n = 8
    est, err = creutz_string_tension([w(1, 1)] * n, [w(1, 2)] * n, [w(2, 2)] * n)
    assert abs(est - sigma) < 1e-12
    assert err < 1e-12
