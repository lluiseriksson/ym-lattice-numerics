from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from scripts.mother_sync_snapshot import build_snapshot

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "mother_sync_snapshot.yml"
CONSTANTS_CONFIG_PATH = ROOT / "configs" / "constants_smoke.yml"
SNAPSHOT_PATH = ROOT / "data" / "processed" / "mother_sync_snapshot.json"
CONSTANTS_PATH = ROOT / "CONSTANTS.md"
MATHLIB_AUDIT_PATH = ROOT / "MATHLIB_AUDIT.md"
README_PATH = ROOT / "README.md"
DIGEST_PATH = ROOT / "docs" / "MOTHER_DIGEST.md"
STATUS_PATH = ROOT / "docs" / "STATUS.md"

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    assert isinstance(document, dict)
    return document


def test_mother_sync_snapshot_matches_generator() -> None:
    committed = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert committed == build_snapshot(CONFIG_PATH)
    assert committed["schema_version"] == 1
    assert SHA_RE.match(committed["sidecar"]["audited_head"])
    assert SHA_RE.match(committed["mother"]["commit"])
    assert SHA_RE.match(committed["mother"]["mathlib_commit"])
    assert "source construction" in committed["honesty"]
    assert "mass-gap claim" in committed["honesty"]


def test_mother_sync_snapshot_agrees_with_constants_config() -> None:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    constants = _read_yaml(CONSTANTS_CONFIG_PATH)

    assert constants["mother"] == {
        "repo": snapshot["mother"]["repo"],
        "branch": snapshot["mother"]["branch"],
        "commit": snapshot["mother"]["commit"],
        "lean_toolchain": snapshot["mother"]["lean_toolchain"],
        "mathlib_commit": snapshot["mother"]["mathlib_commit"],
    }


def test_mother_sync_snapshot_is_documented_on_mother_facing_surfaces() -> None:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    required_tokens = {
        snapshot["sidecar"]["audited_head"],
        snapshot["mother"]["commit"],
        snapshot["mother"]["lean_toolchain"],
        snapshot["mother"]["mathlib_commit"],
        "data/processed/mother_sync_snapshot.json",
    }
    documents = [
        CONSTANTS_PATH.read_text(encoding="utf-8"),
        MATHLIB_AUDIT_PATH.read_text(encoding="utf-8"),
        README_PATH.read_text(encoding="utf-8"),
        DIGEST_PATH.read_text(encoding="utf-8"),
        STATUS_PATH.read_text(encoding="utf-8"),
    ]

    for token in required_tokens:
        assert any(token in document for document in documents), token

    for document in documents:
        assert snapshot["mother"]["commit"] in document
