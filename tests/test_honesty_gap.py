from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ym_lattice_numerics.constants import kp_sigma_lhs
from ym_lattice_numerics.exact2d import string_tension_exact_interval
from ym_lattice_numerics.intervals import Interval, certify_less


ROOT = Path(__file__).resolve().parents[1]
HONESTY_GAP_PATH = ROOT / "data" / "processed" / "honesty_gap_2d.json"


def test_window_certifiably_fails_at_physical_coupling() -> None:
    sigma = string_tension_exact_interval("1", terms=60)
    lhs = kp_sigma_lhs(Interval.parse("2"), sigma)
    assert certify_less(lhs, Interval.parse("1")) == "fail"


def test_window_certifiably_passes_deep_in_weak_coupling() -> None:
    sigma = string_tension_exact_interval("2000", terms=1400)
    lhs = kp_sigma_lhs(Interval.parse("2"), sigma)
    assert certify_less(lhs, Interval.parse("1")) == "pass"


def test_honesty_gap_report_matches_regenerated_script_output(tmp_path: Path) -> None:
    generated_path = tmp_path / "honesty_gap_2d.json"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "honesty_gap_2d.py"),
            "--output",
            str(generated_path),
        ],
        cwd=ROOT,
        check=True,
    )

    committed_report = json.loads(HONESTY_GAP_PATH.read_text(encoding="utf-8"))
    generated_report = json.loads(generated_path.read_text(encoding="utf-8"))

    assert generated_report == committed_report
