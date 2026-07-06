from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def build_snapshot(config_path: Path = ROOT / "configs" / "mother_sync_snapshot.yml") -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise ValueError("mother sync snapshot config must contain a YAML mapping")

    required = {"schema_version", "audited_at", "honesty", "sidecar", "mother", "observed_by", "notes"}
    missing = required - set(document)
    if missing:
        raise ValueError(f"missing snapshot fields: {sorted(missing)!r}")

    return {
        "schema_version": document["schema_version"],
        "audited_at": document["audited_at"],
        "honesty": document["honesty"],
        "sidecar": document["sidecar"],
        "mother": document["mother"],
        "observed_by": document["observed_by"],
        "notes": document["notes"],
    }


def write_snapshot(snapshot: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "mother_sync_snapshot.yml",
        help="YAML snapshot metadata config.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "processed" / "mother_sync_snapshot.json",
        help="JSON snapshot output path.",
    )
    args = parser.parse_args(argv)

    snapshot = build_snapshot(args.config)
    write_snapshot(snapshot, args.output)
    print(json.dumps(snapshot, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
