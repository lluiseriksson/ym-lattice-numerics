from __future__ import annotations

from ym_lattice_numerics.constants import kp_sigma_lhs
from ym_lattice_numerics.exact2d import string_tension_exact_interval
from ym_lattice_numerics.intervals import Interval, certify_less


def test_window_certifiably_fails_at_physical_coupling() -> None:
    sigma = string_tension_exact_interval("1", terms=60)
    lhs = kp_sigma_lhs(Interval.parse("2"), sigma)
    assert certify_less(lhs, Interval.parse("1")) == "fail"


def test_window_certifiably_passes_deep_in_weak_coupling() -> None:
    sigma = string_tension_exact_interval("2000", terms=1400)
    lhs = kp_sigma_lhs(Interval.parse("2"), sigma)
    assert certify_less(lhs, Interval.parse("1")) == "pass"
