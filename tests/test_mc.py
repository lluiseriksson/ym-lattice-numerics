from __future__ import annotations

from ym_lattice_numerics.mc import run_config


def test_minimal_mc_run() -> None:
    result = run_config(
        {
            "description": "test",
            "honesty": "test only",
            "seed": 1,
            "start": "cold",
            "lattice": {"length": 2, "ndim": 4},
            "beta_values": [0.25],
            "updates": {
                "thermalization_sweeps": 1,
                "measurements": 1,
                "sweeps_between_measurements": 1,
                "overrelaxation_per_heatbath": 0,
            },
            "wilson_loops": [[1, 1]],
            "creutz_ratios": [],
        }
    )
    assert result["schema_version"] == 1
    assert len(result["runs"]) == 1
    assert len(result["runs"][0]["samples"]) == 1
