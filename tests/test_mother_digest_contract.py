from __future__ import annotations

import importlib
import json
import re
from decimal import Decimal
from pathlib import Path

from scripts.honesty_gap_2d import build_report


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "data" / "processed" / "honesty_gap_2d.json"
MANIFEST_PATH = ROOT / "data" / "processed" / "artifact_manifest.json"
DIGEST_PATH = ROOT / "docs" / "MOTHER_DIGEST.md"
REPRODUCIBILITY_PATH = ROOT / "REPRODUCIBILITY.md"
STATUS_PATH = ROOT / "docs" / "STATUS.md"

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

COMMIT_SHA_RE = re.compile(r"`([0-9a-f]{40})`")

MODULE_API_SURFACES = {
    "ym_lattice_numerics.exact2d": {
        "file": "src/ym_lattice_numerics/exact2d.py",
        "names": {
            "bessel_i_interval",
            "plaquette_exact_interval",
            "string_tension_exact_interval",
            "bessel_i",
            "plaquette_exact",
            "string_tension_exact",
            "strong_coupling_plaquette",
        },
    },
    "ym_lattice_numerics.intervals": {
        "file": "src/ym_lattice_numerics/intervals.py",
        "names": {
            "Interval",
            "sum_intervals",
            "certify_less",
        },
    },
    "ym_lattice_numerics.analysis": {
        "file": "src/ym_lattice_numerics/analysis.py",
        "names": {
            "jackknife",
            "binned_series",
            "binned_error",
            "creutz_string_tension",
            "effective_mass",
        },
    },
}

INTERVAL_METHODS = {
    "point",
    "parse",
    "reciprocal",
    "pow_int",
    "ln",
}


def _assert_decimal_interval(value: object) -> None:
    assert isinstance(value, list)
    assert len(value) == 2
    lo, hi = value
    assert isinstance(lo, str)
    assert isinstance(hi, str)
    assert Decimal(lo) <= Decimal(hi)


def _first_documented_sha(text: str) -> str:
    match = COMMIT_SHA_RE.search(text)
    assert match
    return match.group(1)


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


def test_mother_digest_and_status_audit_same_main_head() -> None:
    digest = DIGEST_PATH.read_text(encoding="utf-8")
    status = STATUS_PATH.read_text(encoding="utf-8")

    assert _first_documented_sha(digest) == _first_documented_sha(status)


def test_honesty_gap_report_is_fresh_against_generator() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert report == build_report()


def test_honesty_gap_regeneration_command_is_documented() -> None:
    reproducibility = REPRODUCIBILITY_PATH.read_text(encoding="utf-8")

    assert "python scripts\\honesty_gap_2d.py --output data\\processed\\honesty_gap_2d.json" in reproducibility
    assert "`data/processed/honesty_gap_2d.json`" in reproducibility
    assert "separate from `scripts/regenerate_all.py`" in reproducibility


def test_artifact_manifest_is_surfaced_in_mother_digest() -> None:
    digest = DIGEST_PATH.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    for field in {
        "schema_version",
        "honesty",
        "artifacts[]",
        "id",
        "scope",
        "producer",
        "command_argv",
        "inputs",
        "outputs",
        "verification",
        "stdout_log",
    }:
        assert field in digest

    for artifact in manifest["artifacts"]:
        assert artifact["id"] in digest
        assert artifact["scope"] in digest
        for output_path in artifact["outputs"]:
            assert output_path in digest


def test_aqft_manifest_contract_is_surfaced_in_mother_digest() -> None:
    digest = DIGEST_PATH.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    aqft_artifacts = [
        artifact
        for artifact in manifest["artifacts"]
        if artifact["id"] in {"aqft_gaussian_covariance", "aqft_transfer_gap"}
    ]
    assert len(aqft_artifacts) == 2

    for artifact in aqft_artifacts:
        assert artifact["id"] in digest
        assert artifact["producer"] in digest
        assert artifact["command_argv"][:2] == ["python", artifact["producer"]]
        assert "--output" in artifact["command_argv"]
        assert " ".join(artifact["command_argv"][:3]) in digest
        assert artifact["stdout_log"] in artifact["outputs"]

    for phrase in {
        "temporary certificate path",
        "audit-only outputs",
        "build_certificate()",
        "floating-point last-bit drift",
    }:
        assert phrase in digest


def test_mother_digest_documented_python_apis_exist() -> None:
    digest = DIGEST_PATH.read_text(encoding="utf-8")

    for module_name, surface in MODULE_API_SURFACES.items():
        module = importlib.import_module(module_name)
        assert surface["file"] in digest
        for public_name in surface["names"]:
            assert public_name in digest
            assert hasattr(module, public_name), f"{module_name}.{public_name}"

    interval_module = importlib.import_module("ym_lattice_numerics.intervals")
    for method_name in INTERVAL_METHODS:
        assert method_name in digest
        assert hasattr(interval_module.Interval, method_name), f"Interval.{method_name}"
