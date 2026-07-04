from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "data" / "processed" / "honesty_gap_2d.json"
DIGEST_PATH = ROOT / "docs" / "MOTHER_DIGEST.md"

TOP_LEVEL_FIELDS = {
    "schema_version",
    "expression",
    "honesty",
    "results",
}

RESULT_FIELDS = {
    "beta",
    "regime",
    "sigma_exact_2d",
    "window_lhs_(16d+1)^2*sigma",
    "certification_lhs_lt_1",
}

EXPECTED_CERTIFICATIONS = {
    "1": "fail",
    "2": "fail",
    "4": "fail",
    "2000": "pass",
}


def _assert_decimal_interval(value: object) -> None:
    assert isinstance(value, list)
    assert len(value) == 2
    lo, hi = value
    assert isinstance(lo, str)
    assert isinstance(hi, str)
    assert Decimal(lo) <= Decimal(hi)


def test_honesty_gap_report_matches_mother_digest_contract() -> None:
    digest = DIGEST_PATH.read_text(encoding="utf-8")
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    for field in TOP_LEVEL_FIELDS | RESULT_FIELDS:
        assert field in digest

    assert TOP_LEVEL_FIELDS <= set(report)
    assert report["schema_version"] == 1
    assert isinstance(report["results"], list)
    assert report["results"]

    certifications = {}
    for row in report["results"]:
        assert RESULT_FIELDS <= set(row)
        _assert_decimal_interval(row["sigma_exact_2d"])
        _assert_decimal_interval(row["window_lhs_(16d+1)^2*sigma"])
        assert row["certification_lhs_lt_1"] in {"pass", "fail", "unknown"}
        certifications[row["beta"]] = row["certification_lhs_lt_1"]

    assert certifications == EXPECTED_CERTIFICATIONS
