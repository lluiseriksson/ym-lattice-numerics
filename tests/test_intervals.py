from __future__ import annotations

from ym_lattice_numerics.constants import run_check
from ym_lattice_numerics.intervals import Interval, certify_less


def test_interval_less_certification() -> None:
    assert certify_less(Interval.parse(["0", "0.9"]), Interval.point("1")) == "pass"
    assert certify_less(Interval.parse(["1", "1.1"]), Interval.point("1")) == "fail"
    assert certify_less(Interval.parse(["0.9", "1.1"]), Interval.point("1")) == "unknown"


def test_kp_sigma_smoke_check_passes() -> None:
    report = run_check(
        {
            "checks": [
                {
                    "id": "example",
                    "expression": "(16*d+1)^2*sigma < 1",
                    "d": ["4", "4"],
                    "sigma": ["0.0001", "0.0001"],
                }
            ]
        }
    )
    assert report["results"][0]["certification"] == "pass"
