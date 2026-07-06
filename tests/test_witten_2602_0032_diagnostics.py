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
