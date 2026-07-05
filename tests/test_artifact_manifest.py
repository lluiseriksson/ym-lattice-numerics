from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "processed" / "artifact_manifest.json"
REPRODUCIBILITY_PATH = ROOT / "REPRODUCIBILITY.md"


def _normalized_command_text(text: str) -> str:
    return text.replace("\\", "/")


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
