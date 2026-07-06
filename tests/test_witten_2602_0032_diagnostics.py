from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

from scripts.witten_2602_0032_diagnostics import build_report


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "data" / "processed" / "witten_2602_0032_diagnostics.json"


def test_witten_2602_0032_report_matches_generator() -> None:
    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert committed == build_report()


def test_witten_2602_0032_hessian_diagnostics_are_explicit() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    diagnostic = report["diagnostics"]["wilson_hessian_su2_2x2x2"]

    assert report["schema_version"] == 1
    assert "Numerical sidecar diagnostics only" in report["honesty"]
    assert diagnostic["variables"] == 72

    theta_zero = diagnostic["theta_zero"]
    assert theta_zero["kernel_dimension"] == 30
    assert theta_zero["flat_tangent_dimension_reference"] == 24
    assert theta_zero["nonzero_eigenvalues_unique"] == [2.0, 4.0, 6.0]
    assert theta_zero["max_abs_deviation_from_maxwell_reference"] < 1e-4

    toron = diagnostic["quartic_toron_ratio"]
    assert math.isclose(toron["ratio"], 16.0, rel_tol=0.0, abs_tol=0.05)

    generic = diagnostic["generic_theta"]
    assert generic["theta"] == [0.53, 0.91, 0.36]
    assert generic["kernel_dimension"] == 26
    assert generic["min_positive_eigenvalue"] > 0.1


def test_witten_2602_0032_born_oppenheimer_diagnostics_are_explicit() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    diagnostic = report["diagnostics"]["born_oppenheimer_vbo_lemma_5_2"]

    assert "proof-formula versus literal-formula mismatch" in diagnostic["consumption_limit"]
    assert diagnostic["versions"]["proof"] == "omega^2 = khat^2 + m_a(theta)^2"
    assert (
        diagnostic["versions"]["literal"]
        == "paper-v1 literal equations (2)+(3) inside sin^2"
    )

    rows = diagnostic["hessian_rows"]
    assert [(row["Nc"], row["L"], row["variables"]) for row in rows] == [
        (2, 4, 3),
        (2, 8, 3),
        (3, 4, 6),
    ]
    for row in rows:
        assert math.isclose(
            row["proof_hessian_diag_over_S1"],
            row["proof_expected_diag_over_S1"],
            rel_tol=0.0,
            abs_tol=1e-6,
        )
        assert row["proof_max_relative_deviation_from_Nc_S1_identity"] < 1e-6
        assert row["literal_hessian_diag"] < 0.0
        assert row["literal_max_eigenvalue"] < 0.0

    grid_scan = diagnostic["grid_scan"]
    assert grid_scan["case"] == "SU(2), L=4, grid 15^3"
    assert grid_scan["proof_min_off_coroot_lattice"] > 9.0
    assert grid_scan["literal_min"] < -2.0
    assert grid_scan["literal_argmin"] == [
        -4.442882938158,
        -4.442882938158,
        -4.442882938158,
    ]


def test_witten_2602_0032_cli_writes_same_report(tmp_path: Path) -> None:
    generated = tmp_path / "witten_2602_0032_diagnostics.json"

    subprocess.run(
        [
            sys.executable,
            "scripts/witten_2602_0032_diagnostics.py",
            "--output",
            str(generated),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(generated.read_text(encoding="utf-8")) == json.loads(
        REPORT_PATH.read_text(encoding="utf-8")
    )
