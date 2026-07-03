from __future__ import annotations

import math

from ym_lattice_numerics.exact2d import (
    bessel_i,
    bessel_i_interval,
    plaquette_exact,
    plaquette_exact_interval,
    string_tension_exact_interval,
)
from ym_lattice_numerics.intervals import Interval


def test_bessel_recurrence_certified() -> None:
    # I_0(x) - I_2(x) = (2/x) I_1(x): the certified enclosures must overlap.
    for beta in ("0.5", "1", "2", "3.5"):
        i0 = bessel_i_interval(0, beta, terms=50)
        i2 = bessel_i_interval(2, beta, terms=50)
        i1 = bessel_i_interval(1, beta, terms=50)
        lhs = i0 - i2
        rhs = Interval.parse("2") / Interval.parse(beta) * i1
        assert lhs.lo <= rhs.hi and rhs.lo <= lhs.hi, (beta, lhs, rhs)


def test_bessel_known_value() -> None:
    # I_1(1) = 0.565159103992485... (Abramowitz-Stegun 9.8)
    iv = bessel_i_interval(1, "1", terms=50)
    assert float(iv.lo) <= 0.565159103992485 <= float(iv.hi)
    assert float(iv.hi) - float(iv.lo) < 1e-30


def test_plaquette_small_beta_strong_coupling() -> None:
    # I_2/I_1 = beta/4 + O(beta^3)
    beta = 0.05
    assert abs(plaquette_exact(beta) - beta / 4) < 1e-4


def test_plaquette_interval_is_tight_and_in_unit_range() -> None:
    iv = plaquette_exact_interval("1", terms=50)
    assert 0 < float(iv.lo) <= float(iv.hi) < 1
    assert float(iv.hi) - float(iv.lo) < 1e-25


def test_string_tension_matches_float_log() -> None:
    iv = string_tension_exact_interval("1", terms=50)
    expected = -math.log(plaquette_exact(1.0, terms=50))
    assert float(iv.lo) <= expected <= float(iv.hi)
    assert float(iv.lo) > 0  # confining at beta = 1


def test_interval_ln_brackets_math_log() -> None:
    iv = Interval.parse(["2", "2"]).ln()
    assert float(iv.lo) <= math.log(2.0) <= float(iv.hi)
