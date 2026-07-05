from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
from pathlib import Path

from ym_lattice_numerics.mc import run_from_file


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "processed" / "artifact_manifest.json"
REPRODUCIBILITY_PATH = ROOT / "REPRODUCIBILITY.md"


def _normalized_command_text(text: str) -> str:
    return text.replace("\\", "/")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _assert_smoke_payload_close(generated, committed) -> None:
    if isinstance(committed, dict):
        assert isinstance(generated, dict)
        assert generated.keys() == committed.keys()
        for key in committed:
            _assert_smoke_payload_close(generated[key], committed[key])
        return

    if isinstance(committed, list):
        assert isinstance(generated, list)
        assert len(generated) == len(committed)
        for generated_item, committed_item in zip(generated, committed):
            _assert_smoke_payload_close(generated_item, committed_item)
        return

    if isinstance(committed, float):
        assert isinstance(generated, float | int)
        assert math.isclose(generated, committed, rel_tol=0.0, abs_tol=1e-5)
        return

    assert generated == committed


def _assert_smoke_csv_rows_close(generated_rows: list[dict[str, str]], committed_rows: list[dict[str, str]]) -> None:
    assert len(generated_rows) == len(committed_rows)
    for generated_row, committed_row in zip(generated_rows, committed_rows):
        assert generated_row.keys() == committed_row.keys()
        for key in committed_row:
            generated_value = generated_row[key]
            committed_value = committed_row[key]
            try:
                generated_float = float(generated_value)
                committed_float = float(committed_value)
            except ValueError:
                assert generated_value == committed_value
            else:
                assert math.isclose(generated_float, committed_float, rel_tol=0.0, abs_tol=1e-5), key


def test_artifact_manifest_paths_and_commands_are_current() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 1
    artifacts = manifest["artifacts"]
    assert artifacts

    seen_ids = set()
    produced_outputs = set()
    for artifact in artifacts:
        seen_ids.add(artifact["id"])
        assert artifact["command_argv"][:2] == ["python", artifact["producer"]]
        assert (ROOT / artifact["producer"]).is_file()
        assert artifact["outputs"]
        assert artifact["verification"]

        for input_path in artifact["inputs"]:
            assert (ROOT / input_path).exists()
        for output_path in artifact["outputs"]:
            assert (ROOT / output_path).exists()
            assert output_path not in produced_outputs
            produced_outputs.add(output_path)
        if stdout_log := artifact.get("stdout_log"):
            assert stdout_log in artifact["outputs"]
            log_text = (ROOT / stdout_log).read_text(encoding="utf-8").strip()
            assert log_text
            assert "certificate written:" in log_text

            non_log_outputs = [path for path in artifact["outputs"] if path != stdout_log]
            assert non_log_outputs
            assert any(Path(path).name in log_text for path in non_log_outputs)

    assert len(seen_ids) == len(artifacts)
    assert "data/processed/honesty_gap_2d.json" in produced_outputs
    assert "data/processed/aqft_bridges/gaussian_covariance_certificate.json" in produced_outputs
    assert "data/processed/aqft_bridges/transfer_gap_certificate.json" in produced_outputs


def test_artifact_manifest_commands_are_documented_for_reproduction() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    reproducibility = _normalized_command_text(REPRODUCIBILITY_PATH.read_text(encoding="utf-8"))

    for artifact in manifest["artifacts"]:
        command = " ".join(artifact["command_argv"])
        assert command in reproducibility, artifact["id"]


def test_artifact_manifest_outputs_are_documented_for_reproduction() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    reproducibility = _normalized_command_text(REPRODUCIBILITY_PATH.read_text(encoding="utf-8"))

    for artifact in manifest["artifacts"]:
        for output_path in artifact["outputs"]:
            assert output_path in reproducibility, (artifact["id"], output_path)


def test_constants_smoke_report_matches_manifest_regeneration(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    artifact = next(
        artifact for artifact in manifest["artifacts"] if artifact["id"] == "constants_smoke_report"
    )
    committed_output = ROOT / artifact["outputs"][0]
    generated_output = tmp_path / Path(artifact["outputs"][0]).name

    command = list(artifact["command_argv"])
    assert command == ["python", "scripts/check_constants.py", "configs/constants_smoke.yml"]
    command[0] = sys.executable
    command.extend(["--output", str(generated_output)])

    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)

    committed_report = json.loads(committed_output.read_text(encoding="utf-8"))
    generated_report = json.loads(generated_output.read_text(encoding="utf-8"))

    assert generated_report == committed_report


def test_m0_smoke_dataset_matches_manifest_regeneration(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    artifact = next(artifact for artifact in manifest["artifacts"] if artifact["id"] == "m0_su2_smoke")

    assert artifact["command_argv"] == [
        "python",
        "scripts/regenerate_all.py",
        "--config",
        "configs/m0_su2_smoke.yml",
    ]

    generated_json = tmp_path / "m0_su2_smoke.json"
    generated_csv = tmp_path / "m0_su2_smoke.csv"
    run_from_file(ROOT / artifact["inputs"][0], generated_json, generated_csv)

    committed_json = ROOT / "data/raw/m0_su2_smoke.json"
    committed_csv = ROOT / "data/raw/m0_su2_smoke.csv"

    _assert_smoke_payload_close(
        json.loads(generated_json.read_text(encoding="utf-8")),
        json.loads(committed_json.read_text(encoding="utf-8")),
    )
    _assert_smoke_csv_rows_close(_read_csv_rows(generated_csv), _read_csv_rows(committed_csv))
