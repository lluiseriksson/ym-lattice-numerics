from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path


NC = 2
BETA_VALUES = [10.0, 20.0, 40.0]
H_DOB_PARAMETERS = {
    "dimension": 4,
    "M": 2.0,
    "r": 0.5,
    "gamma0": 1.0,
    "c_gamma_power": 2,
    "fixed_kappa_exhibit": 250.0,
}
FOUR_ROTOR_ENTROPY_PARAMETERS = {
    "rotor_count": 4,
    "grid_points_per_rotor": 8,
    "beta": 0.75,
}
ROTHAUS_ALPHA_PARAMETERS = {
    "alpha_grid": [0.125, 0.25, 0.5, 0.75, 0.875],
    "base_lsi_constant": 2.0,
    "defect_weight": 0.25,
}
DEFECT_LSI_BUDGET_PARAMETERS = {
    "base_lsi_constant": 2.0,
    "defect_grid": [0.03125, 0.0625, 0.125, 0.25, 0.5],
    "max_relative_loss": 0.25,
}
UNIFORM_POINCARE_PARAMETERS = {
    "cycle_points": 8,
    "fourier_mode": 1,
}
POLYMER_COUNTING_PARAMETERS = {
    "dimension": 4,
    "max_size": 6,
    "activity": 1.0 / 32.0,
}


def _rounded(value: float, digits: int = 12) -> float:
    return float(round(float(value), digits))


def _b0(n_colors: int = NC) -> float:
    return 11.0 * n_colors / (24.0 * math.pi**2)


def _c_nc(n_colors: int = NC) -> float:
    return 1.0 / (2.0 * _b0(n_colors))


def _beta_flow_row(beta: float) -> dict[str, object]:
    step = 2.0 * _b0() * math.log(2.0)
    n_max_estimate = beta / step
    n_floor = math.floor(n_max_estimate)
    beta_at_floor = beta - step * n_floor
    beta_at_next = beta - step * (n_floor + 1)
    return {
        "beta": beta,
        "b0_su2": _rounded(_b0()),
        "C_Nc_equals_1_over_2b0": _rounded(_c_nc()),
        "step_2_b0_log2": _rounded(step),
        "n_max_estimate": _rounded(n_max_estimate),
        "n_floor": n_floor,
        "beta_at_n_floor": _rounded(beta_at_floor),
        "beta_at_n_floor_plus_1": _rounded(beta_at_next),
        "floor_brackets_zero": beta_at_floor >= 0.0 and beta_at_next < 0.0,
    }


def _h_dob_window_row(beta: float) -> dict[str, object]:
    flow = _beta_flow_row(beta)
    n_floor = int(flow["n_floor"])
    params = H_DOB_PARAMETERS
    dimension = int(params["dimension"])
    r = float(params["r"])
    log_r_over_one_minus_r_squared = math.log(r) - 2.0 * math.log(1.0 - r)
    c_gamma = float(params["gamma0"]) * (n_floor + 1) ** int(params["c_gamma_power"])
    log_threshold = (
        dimension * (math.log(float(params["M"])) + n_floor * math.log(2.0))
        + math.log(c_gamma)
        + log_r_over_one_minus_r_squared
    )
    fixed_kappa = float(params["fixed_kappa_exhibit"])
    return {
        "beta": beta,
        "n_floor_from_corrected_flow": n_floor,
        "log_R_nmax": _rounded(n_floor * math.log(2.0)),
        "C_Gamma_model": _rounded(c_gamma),
        "threshold_log_rhs": _rounded(log_threshold),
        "fixed_kappa_exhibit": fixed_kappa,
        "fixed_kappa_exceeds_threshold": fixed_kappa > log_threshold,
    }


def _four_rotor_energy(state: tuple[int, ...], grid_points: int) -> float:
    angles = [2.0 * math.pi * index / grid_points for index in state]
    return sum(
        1.0 - math.cos(angles[(index + 1) % len(angles)] - angles[index])
        for index in range(len(angles))
    )


def _four_rotor_entropy_pipeline() -> dict[str, object]:
    params = FOUR_ROTOR_ENTROPY_PARAMETERS
    rotor_count = int(params["rotor_count"])
    grid_points = int(params["grid_points_per_rotor"])
    beta = float(params["beta"])

    energies = [
        _four_rotor_energy(state, grid_points)
        for state in itertools.product(range(grid_points), repeat=rotor_count)
    ]
    weights = [math.exp(-beta * energy) for energy in energies]
    partition = sum(weights)
    probabilities = [weight / partition for weight in weights]
    state_count = grid_points**rotor_count
    uniform_probability = 1.0 / state_count
    shannon_entropy = -sum(
        probability * math.log(probability) for probability in probabilities
    )
    relative_entropy = sum(
        probability * math.log(probability / uniform_probability)
        for probability in probabilities
    )
    mean_energy = sum(
        probability * energy for probability, energy in zip(probabilities, energies)
    )
    identity_residual = relative_entropy - (math.log(state_count) - shannon_entropy)

    return {
        "scope": "finite compact four-rotor entropy pipeline on a discrete torus",
        "parameters": params,
        "state_count": state_count,
        "energy_model": "sum_i (1 - cos(theta_{i+1} - theta_i)) with periodic boundary",
        "gibbs_weight": "exp(-beta*energy)",
        "partition_function": _rounded(partition),
        "mean_energy": _rounded(mean_energy),
        "shannon_entropy": _rounded(shannon_entropy),
        "relative_entropy_to_uniform": _rounded(relative_entropy),
        "entropy_identity": "D(mu||uniform) = log(state_count) - H(mu)",
        "entropy_identity_residual": _rounded(identity_residual),
        "all_probabilities_positive": all(probability > 0.0 for probability in probabilities),
        "min_probability": _rounded(min(probabilities), 15),
        "max_probability": _rounded(max(probabilities), 15),
    }


def _rothaus_alpha_tradeoff() -> dict[str, object]:
    params = ROTHAUS_ALPHA_PARAMETERS
    base_constant = float(params["base_lsi_constant"])
    defect_weight = float(params["defect_weight"])
    rows = []
    for alpha in params["alpha_grid"]:
        alpha = float(alpha)
        constant_multiplier = 1.0 / (1.0 - alpha)
        defect_multiplier = 1.0 / alpha
        rows.append(
            {
                "alpha": alpha,
                "constant_multiplier_1_over_1_minus_alpha": _rounded(
                    constant_multiplier
                ),
                "defect_multiplier_1_over_alpha": _rounded(defect_multiplier),
                "toy_combined_cost": _rounded(
                    base_constant * constant_multiplier
                    + defect_weight * defect_multiplier
                ),
            }
        )

    costs = [float(row["toy_combined_cost"]) for row in rows]
    minimizer_index = min(range(len(costs)), key=costs.__getitem__)
    return {
        "scope": "finite Rothaus-style alpha bookkeeping grid",
        "formula": "toy_cost(alpha) = C0/(1-alpha) + epsilon/alpha",
        "parameters": params,
        "rows": rows,
        "grid_minimizer_alpha": rows[minimizer_index]["alpha"],
        "grid_minimizer_cost": rows[minimizer_index]["toy_combined_cost"],
        "minimizer_is_interior_to_grid": 0 < minimizer_index < len(rows) - 1,
        "constant_multiplier_increases_with_alpha": all(
            left["constant_multiplier_1_over_1_minus_alpha"]
            < right["constant_multiplier_1_over_1_minus_alpha"]
            for left, right in zip(rows, rows[1:])
        ),
        "defect_multiplier_decreases_with_alpha": all(
            left["defect_multiplier_1_over_alpha"]
            > right["defect_multiplier_1_over_alpha"]
            for left, right in zip(rows, rows[1:])
        ),
    }


def _defect_lsi_budget_bookkeeping() -> dict[str, object]:
    params = DEFECT_LSI_BUDGET_PARAMETERS
    base_constant = float(params["base_lsi_constant"])
    max_relative_loss = float(params["max_relative_loss"])

    rows = []
    for defect in params["defect_grid"]:
        defect = float(defect)
        residual = base_constant - defect
        relative_loss = defect / base_constant
        rows.append(
            {
                "defect_epsilon": defect,
                "toy_residual_constant": _rounded(residual),
                "relative_loss": _rounded(relative_loss),
                "residual_is_positive": residual > 0.0,
                "within_budget": relative_loss <= max_relative_loss,
            }
        )

    return {
        "scope": "finite defect-LSI budget bookkeeping grid",
        "formula": "toy_residual_constant = C0 - epsilon",
        "parameters": params,
        "rows": rows,
        "all_residuals_positive": all(row["residual_is_positive"] for row in rows),
        "all_rows_within_relative_budget": all(row["within_budget"] for row in rows),
        "no_defect_lsi_or_tensorization_claim": True,
    }


def _uniform_cycle_poincare_check() -> dict[str, object]:
    params = UNIFORM_POINCARE_PARAMETERS
    cycle_points = int(params["cycle_points"])
    mode = int(params["fourier_mode"])
    values = [
        math.cos(2.0 * math.pi * mode * index / cycle_points)
        for index in range(cycle_points)
    ]
    mean = sum(values) / cycle_points
    centered = [value - mean for value in values]
    variance = sum(value * value for value in centered) / cycle_points
    generator_values = [
        values[index]
        - 0.5 * (values[(index - 1) % cycle_points] + values[(index + 1) % cycle_points])
        for index in range(cycle_points)
    ]
    dirichlet = sum(
        value * generator_value
        for value, generator_value in zip(centered, generator_values)
    ) / cycle_points
    spectral_gap = 1.0 - math.cos(2.0 * math.pi / cycle_points)
    poincare_constant = 1.0 / spectral_gap
    return {
        "scope": "finite uniform Poincare normalization check on Z/NZ",
        "state_space": "cycle graph with uniform measure",
        "operator": "I-P for the nearest-neighbor simple random walk",
        "parameters": params,
        "test_function": "cos(2*pi*mode*x/N)",
        "mean": _rounded(mean),
        "variance": _rounded(variance),
        "dirichlet_form": _rounded(dirichlet),
        "spectral_gap": _rounded(spectral_gap),
        "poincare_constant": _rounded(poincare_constant),
        "mode_saturates_constant": _rounded(
            variance - poincare_constant * dirichlet
        )
        == 0.0,
        "no_lsi_or_defect_claim": True,
    }


def _finite_polymer_counting_bookkeeping() -> dict[str, object]:
    params = POLYMER_COUNTING_PARAMETERS
    dimension = int(params["dimension"])
    max_size = int(params["max_size"])
    activity = float(params["activity"])
    neighbor_choices = 2 * dimension
    ratio = neighbor_choices * activity

    rows = []
    prefix_weight = 0.0
    for size in range(1, max_size + 1):
        walk_encoding_bound = neighbor_choices ** (size - 1)
        weighted_term = walk_encoding_bound * activity**size
        prefix_weight += weighted_term
        rows.append(
            {
                "size": size,
                "walk_encoding_bound": walk_encoding_bound,
                "weighted_term": _rounded(weighted_term, 15),
                "prefix_weight": _rounded(prefix_weight, 15),
            }
        )

    infinite_geometric_envelope = activity / (1.0 - ratio)
    tail_after_max_size = (
        activity * ratio**max_size / (1.0 - ratio) if ratio < 1.0 else math.inf
    )
    return {
        "scope": "finite rooted polymer-counting bookkeeping envelope",
        "parameters": params,
        "encoding": (
            "rooted connected polymer is over-counted by a step sequence with "
            "(2*d)^(size-1) choices"
        ),
        "neighbor_choices_2d": neighbor_choices,
        "activity_ratio_2d_times_activity": _rounded(ratio),
        "ratio_is_subcritical": ratio < 1.0,
        "rows": rows,
        "finite_prefix_weight": _rounded(prefix_weight, 15),
        "tail_after_max_size": _rounded(tail_after_max_size, 15),
        "infinite_geometric_envelope": _rounded(infinite_geometric_envelope, 15),
        "prefix_plus_tail_matches_envelope": _rounded(
            prefix_weight + tail_after_max_size - infinite_geometric_envelope,
            15,
        )
        == 0.0,
        "no_unrooted_polymer_or_activity_claim": True,
    }


def build_report() -> dict[str, object]:
    beta_flow_rows = [_beta_flow_row(beta) for beta in BETA_VALUES]
    h_dob_rows = [_h_dob_window_row(beta) for beta in BETA_VALUES]
    thresholds = [row["threshold_log_rhs"] for row in h_dob_rows]

    report = {
        "schema_version": 1,
        "source": "2602.0041 v3 deterministic LSI/H-DOB verifier boundary subset",
        "honesty": (
            "Numerical sidecar contract only. This report does not discharge H-XSD "
            "or H-DOB, does not verify companion papers 2602.0054-2602.0057, and "
            "does not prove source construction, hRpoly, continuum construction, "
            "a mass gap, or Clay."
        ),
        "diagnostics": {
            "ricci_convention": {
                "group": "SU(2)",
                "formula": "Ric = Nc/2",
                "Nc": NC,
                "value": _rounded(NC / 2.0),
                "expected_value": 1.0,
                "coherent": _rounded(NC / 2.0) == 1.0,
            },
            "corrected_beta_flow": {
                "formula": "beta_k = beta - 2*b0*k*log(2)",
                "n_max_formula": "n_max ~= beta/(2*b0*log(2)) = beta*C(Nc)/log(2)",
                "rows": beta_flow_rows,
            },
            "geometric_sum": {
                "r": H_DOB_PARAMETERS["r"],
                "formula": "sum_{n>=1} n*r^n = r/(1-r)^2",
                "closed_value": _rounded(
                    H_DOB_PARAMETERS["r"] / (1.0 - H_DOB_PARAMETERS["r"]) ** 2
                ),
            },
            "h_dob_kappa_window_exhibit": {
                "threshold_shape": (
                    "kappa > log[((M R_nmax)^d C_Gamma r)/(1-r)^2]"
                ),
                "parameters": H_DOB_PARAMETERS,
                "rows": h_dob_rows,
                "threshold_increases_over_beta_grid": all(
                    left < right for left, right in zip(thresholds, thresholds[1:])
                ),
            },
            "compact_four_rotor_entropy_pipeline": _four_rotor_entropy_pipeline(),
            "rothaus_alpha_tradeoff": _rothaus_alpha_tradeoff(),
            "defect_lsi_budget_bookkeeping": _defect_lsi_budget_bookkeeping(),
            "uniform_cycle_poincare_check": _uniform_cycle_poincare_check(),
            "finite_polymer_counting_bookkeeping": (
                _finite_polymer_counting_bookkeeping()
            ),
        },
    }
    return report


def write_report(report: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/verify_2602_0041_report.json"),
    )
    args = parser.parse_args(argv)
    write_report(build_report(), args.output)
    print(f"2602.0041 diagnostics written: {args.output}")


if __name__ == "__main__":
    main()
