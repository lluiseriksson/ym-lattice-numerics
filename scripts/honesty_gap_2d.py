"""M4 honesty-gap report for the exactly soluble 2D theory.

Evaluates the mother repository's formal constant window
``(16 d + 1)^2 sigma < 1`` at ``d = 2`` against the CERTIFIED exact 2D
string tension ``sigma(beta) = -log(I_2(beta)/I_1(beta))``, over both the
physically interesting couplings and the weak-coupling region where the
window finally opens.  The expected (and found) answer: the formal window
sits orders of magnitude away from the physical couplings.  Quantifying
that gap, with interval certificates on both sides, is the M4 deliverable.

Usage: python scripts/honesty_gap_2d.py [--output data/processed/honesty_gap_2d.json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ym_lattice_numerics.constants import kp_sigma_lhs
from ym_lattice_numerics.exact2d import string_tension_exact_interval
from ym_lattice_numerics.intervals import Interval, certify_less


CASES = [
    {"beta": "1", "terms": 60, "regime": "physical (strong coupling)"},
    {"beta": "2", "terms": 60, "regime": "physical"},
    {"beta": "4", "terms": 80, "regime": "physical (scaling window in 4D lore)"},
    {"beta": "2000", "terms": 1400, "regime": "formal window candidate (weak coupling)"},
]


def build_report() -> dict:
    d = Interval.parse("2")
    one = Interval.parse("1")
    rows = []
    for case in CASES:
        sigma = string_tension_exact_interval(case["beta"], terms=int(case["terms"]))
        lhs = kp_sigma_lhs(d, sigma)
        rows.append(
            {
                "beta": case["beta"],
                "regime": case["regime"],
                "sigma_exact_2d": sigma.to_json(),
                "window_lhs_(16d+1)^2*sigma": lhs.to_json(),
                "certification_lhs_lt_1": certify_less(lhs, one),
            }
        )
    return {
        "schema_version": 1,
        "expression": "(16*d+1)^2*sigma < 1 at d = 2, sigma = -log(I2(beta)/I1(beta)) certified",
        "honesty": (
            "Exact 2D theory only: sigma is the certified infinite-volume 2D "
            "string tension, a stand-in for the 4D constants the mother's KP "
            "window actually concerns. The point being quantified is the "
            "orders-of-magnitude distance between where the formal window "
            "certifiably opens and the physically studied couplings."
        ),
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("data/processed/honesty_gap_2d.json"))
    args = parser.parse_args()
    report = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(
        [{k: r[k] for k in ("beta", "certification_lhs_lt_1")} for r in report["results"]],
        indent=2))


if __name__ == "__main__":
    main()
