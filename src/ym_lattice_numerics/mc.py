"""Command-line Monte Carlo runner for small reproducible SU(2) ensembles."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from . import __version__
from .lattice import LatticeSpec, cold_start, heatbath_sweep, hot_start, mean_plaquette, overrelaxation_sweep
from .observables import creutz_ratio_from_links, mean_wilson_loop


def _rng_for(seed: int, beta_index: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([seed, beta_index]))


def _apply_update_cycle(links: np.ndarray, beta: float, rng: np.random.Generator, overrelax: int) -> None:
    heatbath_sweep(links, beta, rng)
    for _ in range(overrelax):
        overrelaxation_sweep(links)


def run_config(config: dict[str, Any]) -> dict[str, Any]:
    """Run a Monte Carlo configuration and return a JSON-serializable result."""

    lattice_cfg = config["lattice"]
    spec = LatticeSpec(length=int(lattice_cfg["length"]), ndim=int(lattice_cfg.get("ndim", 4)))
    seed = int(config["seed"])
    update_cfg = config["updates"]
    therm = int(update_cfg["thermalization_sweeps"])
    measurements = int(update_cfg["measurements"])
    between = int(update_cfg["sweeps_between_measurements"])
    overrelax = int(update_cfg.get("overrelaxation_per_heatbath", 0))
    start = config.get("start", "hot")
    loop_extents = [tuple(map(int, item)) for item in config.get("wilson_loops", [])]
    creutz_extents = [tuple(map(int, item)) for item in config.get("creutz_ratios", [])]

    runs = []
    for beta_index, beta_raw in enumerate(config["beta_values"]):
        beta = float(beta_raw)
        rng = _rng_for(seed, beta_index)
        links = cold_start(spec) if start == "cold" else hot_start(spec, rng)

        for _ in range(therm):
            _apply_update_cycle(links, beta, rng, overrelax)

        samples = []
        for measurement_index in range(measurements):
            for _ in range(between):
                _apply_update_cycle(links, beta, rng, overrelax)
            sample: dict[str, Any] = {
                "measurement": measurement_index,
                "plaquette": mean_plaquette(links),
            }
            for r, t in loop_extents:
                sample[f"wilson_{r}x{t}"] = mean_wilson_loop(links, r, t)
            for r, t in creutz_extents:
                sample[f"creutz_{r}x{t}"] = creutz_ratio_from_links(links, r, t)
            samples.append(sample)

        plaquettes = np.array([sample["plaquette"] for sample in samples], dtype=np.float64)
        runs.append(
            {
                "beta": beta,
                "seed_sequence": [seed, beta_index],
                "plaquette_mean": float(np.mean(plaquettes)),
                "plaquette_std": float(np.std(plaquettes, ddof=1)) if len(plaquettes) > 1 else 0.0,
                "samples": samples,
            }
        )

    return {
        "schema_version": 1,
        "package_version": __version__,
        "description": config.get("description", ""),
        "honesty": config.get("honesty", "unspecified"),
        "config": config,
        "runs": runs,
    }


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("configuration must be a YAML mapping")
    return config


def write_json(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for run in result["runs"]:
        rows.append(
            {
                "beta": run["beta"],
                "plaquette_mean": run["plaquette_mean"],
                "plaquette_std": run["plaquette_std"],
                "measurements": len(run["samples"]),
            }
        )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["beta", "plaquette_mean", "plaquette_std", "measurements"])
        writer.writeheader()
        writer.writerows(rows)


def run_from_file(config_path: Path, output_json: Path | None = None, output_csv: Path | None = None) -> dict[str, Any]:
    config = load_config(config_path)
    result = run_config(config)
    run_id = config.get("run_id", config_path.stem)
    if output_json is None:
        output_json = Path("data/raw") / f"{run_id}.json"
    if output_csv is None:
        output_csv = Path("data/raw") / f"{run_id}.csv"
    write_json(result, output_json)
    write_csv(result, output_csv)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-csv", type=Path, default=None)
    args = parser.parse_args(argv)

    result = run_from_file(args.config, args.output_json, args.output_csv)
    print(json.dumps({"runs": result["runs"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
