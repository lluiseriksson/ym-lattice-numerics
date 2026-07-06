from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ym_lattice_numerics.mc import run_from_file


def write_plaquette_figure(result: dict, path: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("matplotlib is required for figure regeneration; install .[plot]") from exc

    betas = [run["beta"] for run in result["runs"]]
    means = [run["plaquette_mean"] for run in result["runs"]]
    stds = [run["plaquette_std"] for run in result["runs"]]

    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.0, 4.0), constrained_layout=True)
    ax.errorbar(betas, means, yerr=stds, marker="o", capsize=4, linewidth=1.4)
    ax.set_xlabel("beta")
    ax.set_ylabel("mean plaquette")
    ax.set_title("SU(2) Wilson smoke run")
    ax.grid(True, alpha=0.25)
    ax.set_ylim(-0.2, 1.05)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/m0_su2_smoke.yml"))
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-csv", type=Path, default=None)
    parser.add_argument("--output-figure", type=Path, default=None)
    args = parser.parse_args(argv)

    result = run_from_file(args.config, args.output_json, args.output_csv)
    run_id = result["config"].get("run_id", args.config.stem)
    figure_path = args.output_figure or Path("figures") / f"{run_id}_plaquette.png"
    write_plaquette_figure(result, figure_path)


if __name__ == "__main__":
    main()
