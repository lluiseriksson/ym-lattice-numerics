"""Executable interval checks for explicit constants."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from .intervals import Interval, certify_less


def kp_sigma_lhs(d: Interval, sigma: Interval) -> Interval:
    """Compute the interval ``(16d + 1)^2 sigma``."""

    return ((16 * d + 1).pow_int(2)) * sigma


def run_check(document: dict[str, Any]) -> dict[str, Any]:
    """Run all interval checks in a constants YAML document."""

    results = []
    for item in document.get("checks", []):
        expression = item.get("expression")
        if expression != "(16*d+1)^2*sigma < 1":
            raise ValueError(f"unsupported expression: {expression!r}")
        d = Interval.parse(item["d"])
        sigma = Interval.parse(item["sigma"])
        rhs = Interval.parse(item.get("rhs", "1"))
        lhs = kp_sigma_lhs(d, sigma)
        results.append(
            {
                "id": item["id"],
                "status": item.get("status", "unspecified"),
                "expression": expression,
                "d": d.to_json(),
                "sigma": sigma.to_json(),
                "lhs": lhs.to_json(),
                "rhs": rhs.to_json(),
                "certification": certify_less(lhs, rhs),
                "provenance": item.get("provenance", "unspecified"),
            }
        )
    return {
        "mother": document.get("mother", {}),
        "results": results,
    }


def check_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise ValueError("constants file must contain a YAML mapping")
    return run_check(document)


def write_report(report: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("constants_file", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON report path; default derives from constants file name.",
    )
    args = parser.parse_args(argv)

    report = check_file(args.constants_file)
    output = args.output
    if output is None:
        output = Path("data/processed") / f"{args.constants_file.stem}_report.json"
    write_report(report, output)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
