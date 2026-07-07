from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.verify_2602_0041 import build_report


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "data" / "processed" / "verify_2602_0041_report.json"


def test_verify_2602_0041_report_matches_generator() -> None:
    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert committed == build_report()


def test_verify_2602_0041_contract_boundaries_are_explicit() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    diagnostics = report["diagnostics"]

    assert report["schema_version"] == 1
    assert "does not discharge H-XSD or H-DOB" in report["honesty"]
    assert "does not prove source construction" in report["honesty"]

    ricci = diagnostics["ricci_convention"]
    assert ricci["formula"] == "Ric = Nc/2"
    assert ricci["value"] == 1.0
    assert ricci["coherent"] is True

    flow_rows = diagnostics["corrected_beta_flow"]["rows"]
    assert [row["beta"] for row in flow_rows] == [10.0, 20.0, 40.0]
    for row in flow_rows:
        assert row["floor_brackets_zero"] is True
        assert row["C_Nc_equals_1_over_2b0"] > 0.0
        assert row["n_max_estimate"] > 0.0

    geometric = diagnostics["geometric_sum"]
    assert geometric["formula"] == "sum_{n>=1} n*r^n = r/(1-r)^2"
    assert geometric["closed_value"] == 2.0


def test_verify_2602_0041_h_dob_window_exhibit_is_monotone() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    window = report["diagnostics"]["h_dob_kappa_window_exhibit"]
    rows = window["rows"]

    assert window["threshold_increases_over_beta_grid"] is True
    assert [row["beta"] for row in rows] == [10.0, 20.0, 40.0]
    thresholds = [row["threshold_log_rhs"] for row in rows]
    assert thresholds == sorted(thresholds)
    assert rows[0]["fixed_kappa_exceeds_threshold"] is True
    assert rows[-1]["fixed_kappa_exceeds_threshold"] is False


def test_verify_2602_0041_compact_four_rotor_entropy_pipeline() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    entropy = report["diagnostics"]["compact_four_rotor_entropy_pipeline"]

    assert entropy["scope"] == "finite compact four-rotor entropy pipeline on a discrete torus"
    assert entropy["parameters"] == {
        "rotor_count": 4,
        "grid_points_per_rotor": 8,
        "beta": 0.75,
    }
    assert entropy["state_count"] == 4096
    assert entropy["gibbs_weight"] == "exp(-beta*energy)"
    assert entropy["entropy_identity"] == "D(mu||uniform) = log(state_count) - H(mu)"
    assert entropy["entropy_identity_residual"] == 0.0
    assert entropy["all_probabilities_positive"] is True
    assert 0.0 < entropy["min_probability"] < entropy["max_probability"] < 1.0
    assert entropy["relative_entropy_to_uniform"] > 0.0
    assert entropy["mean_energy"] > 0.0


def test_verify_2602_0041_rothaus_alpha_tradeoff_grid() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    tradeoff = report["diagnostics"]["rothaus_alpha_tradeoff"]
    rows = tradeoff["rows"]

    assert tradeoff["scope"] == "finite Rothaus-style alpha bookkeeping grid"
    assert tradeoff["formula"] == "toy_cost(alpha) = C0/(1-alpha) + epsilon/alpha"
    assert tradeoff["parameters"] == {
        "alpha_grid": [0.125, 0.25, 0.5, 0.75, 0.875],
        "base_lsi_constant": 2.0,
        "defect_weight": 0.25,
    }
    assert [row["alpha"] for row in rows] == tradeoff["parameters"]["alpha_grid"]
    assert tradeoff["grid_minimizer_alpha"] == 0.25
    assert tradeoff["minimizer_is_interior_to_grid"] is True
    assert tradeoff["constant_multiplier_increases_with_alpha"] is True
    assert tradeoff["defect_multiplier_decreases_with_alpha"] is True
    assert rows[0]["toy_combined_cost"] > tradeoff["grid_minimizer_cost"]
    assert rows[-1]["toy_combined_cost"] > tradeoff["grid_minimizer_cost"]


def test_verify_2602_0041_uniform_cycle_poincare_check() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    poincare = report["diagnostics"]["uniform_cycle_poincare_check"]

    assert poincare["scope"] == "finite uniform Poincare normalization check on Z/NZ"
    assert poincare["state_space"] == "cycle graph with uniform measure"
    assert poincare["operator"] == "I-P for the nearest-neighbor simple random walk"
    assert poincare["parameters"] == {
        "cycle_points": 8,
        "fourier_mode": 1,
    }
    assert poincare["test_function"] == "cos(2*pi*mode*x/N)"
    assert poincare["mean"] == 0.0
    assert poincare["variance"] == 0.5
    assert poincare["dirichlet_form"] > 0.0
    assert poincare["spectral_gap"] > 0.0
    assert poincare["poincare_constant"] > 1.0
    assert poincare["mode_saturates_constant"] is True
    assert poincare["no_lsi_or_defect_claim"] is True


def test_verify_2602_0041_cli_writes_same_report(tmp_path: Path) -> None:
    generated = tmp_path / "verify_2602_0041_report.json"

    subprocess.run(
        [
            sys.executable,
            "scripts/verify_2602_0041.py",
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
