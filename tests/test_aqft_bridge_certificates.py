from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = ROOT / "data" / "processed" / "aqft_bridges"
MANIFEST_PATH = ROOT / "data" / "processed" / "artifact_manifest.json"
SCRIPT_DIR = ROOT / "scripts" / "aqft_bridges"


AQFT_BUILDERS = {
    "scripts/aqft_bridges/gaussian_covariance_oracle.py": "gaussian_covariance_oracle",
    "scripts/aqft_bridges/transfer_gap_oracle.py": "transfer_gap_oracle",
}


def _load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _assert_payload_close(committed, rebuilt) -> None:
    if isinstance(committed, dict):
        assert isinstance(rebuilt, dict)
        assert committed.keys() == rebuilt.keys()
        for key in committed:
            _assert_payload_close(committed[key], rebuilt[key])
        return

    if isinstance(committed, list):
        assert isinstance(rebuilt, list)
        assert len(committed) == len(rebuilt)
        for committed_item, rebuilt_item in zip(committed, rebuilt):
            _assert_payload_close(committed_item, rebuilt_item)
        return

    if isinstance(committed, float):
        assert isinstance(rebuilt, float)
        assert math.isclose(committed, rebuilt, rel_tol=0.0, abs_tol=5e-12)
        return

    assert committed == rebuilt


def test_gaussian_covariance_bridge_certificate_schema() -> None:
    payload = json.loads((BRIDGE_DIR / "gaussian_covariance_certificate.json").read_text(encoding="utf-8"))

    assert payload["tool"] == "gaussian_covariance_oracle"
    rows = payload["lattice"]
    assert rows
    assert any(row.get("dim") == 2 for row in rows)
    assert all(row.get("sharp_matches_fit", True) for row in rows)
    assert any(row.get("guardrail") is True for row in rows)


def test_transfer_gap_bridge_certificate_schema() -> None:
    payload = json.loads((BRIDGE_DIR / "transfer_gap_certificate.json").read_text(encoding="utf-8"))

    assert payload["tool"] == "transfer_gap_oracle"
    rows = payload["rows"]
    assert rows
    assert all(row.get("match", True) for row in rows)
    assert any(row.get("guardrail") is True for row in rows)


def test_aqft_bridge_certificate_files_match_builders() -> None:
    gaussian = _load_script("gaussian_covariance_oracle", SCRIPT_DIR / "gaussian_covariance_oracle.py")
    transfer = _load_script("transfer_gap_oracle", SCRIPT_DIR / "transfer_gap_oracle.py")

    committed_gaussian = json.loads(
        (BRIDGE_DIR / "gaussian_covariance_certificate.json").read_text(encoding="utf-8")
    )
    committed_transfer = json.loads(
        (BRIDGE_DIR / "transfer_gap_certificate.json").read_text(encoding="utf-8")
    )

    _assert_payload_close(committed_gaussian, gaussian.build_certificate())
    _assert_payload_close(committed_transfer, transfer.build_certificate())


def test_aqft_manifest_cli_round_trips_match_builders(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    aqft_artifacts = [
        artifact for artifact in manifest["artifacts"] if artifact["producer"] in AQFT_BUILDERS
    ]

    assert {artifact["id"] for artifact in aqft_artifacts} == {
        "aqft_gaussian_covariance",
        "aqft_transfer_gap",
    }

    for artifact in aqft_artifacts:
        command = list(artifact["command_argv"])
        assert command[:2] == ["python", artifact["producer"]]
        assert "--output" in command
        output_index = command.index("--output") + 1
        tmp_output = tmp_path / Path(command[output_index]).name
        command[0] = sys.executable
        command[output_index] = str(tmp_output)

        result = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "certificate written:" in result.stdout

        module = _load_script(AQFT_BUILDERS[artifact["producer"]], ROOT / artifact["producer"])
        generated = json.loads(tmp_output.read_text(encoding="utf-8"))
        _assert_payload_close(generated, module.build_certificate())
