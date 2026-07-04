from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = ROOT / "data" / "processed" / "aqft_bridges"


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
