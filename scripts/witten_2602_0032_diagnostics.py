from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

import numpy as np


def _qmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a0, av = a[..., :1], a[..., 1:]
    b0, bv = b[..., :1], b[..., 1:]
    return np.concatenate(
        [
            a0 * b0 - np.sum(av * bv, -1, keepdims=True),
            a0 * bv + b0 * av - np.cross(av, bv),
        ],
        -1,
    )


def _qconj(a: np.ndarray) -> np.ndarray:
    out = a.copy()
    out[..., 1:] *= -1
    return out


def _wilson_action_batch(x: np.ndarray, theta: tuple[float, float, float]) -> np.ndarray:
    v = x / np.sqrt(2.0)
    angle = np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-300)
    links = np.concatenate([np.cos(angle), np.sin(angle) * v / angle], -1)

    for mu in range(3):
        background = np.zeros(links.shape[:-2] + (4,))
        background[..., 0] = np.cos(theta[mu])
        background[..., 3] = np.sin(theta[mu])
        links[..., mu, :] = _qmul(background, links[..., mu, :])

    action = 0.0
    for mu in range(3):
        for nu in range(mu + 1, 3):
            a = links[..., mu, :]
            b = np.roll(links[..., nu, :], -1, axis=1 + mu)
            c = links[..., nu, :]
            d = np.roll(links[..., mu, :], -1, axis=1 + nu)
            plaquette = _qmul(_qmul(a, b), _qconj(_qmul(c, d)))
            action = action + np.sum(1.0 - plaquette[..., 0], axis=(1, 2, 3))
    return action


def _wilson_hessian(theta: tuple[float, float, float], h: float = 1e-3) -> np.ndarray:
    n_variables = 72
    pairs = [(i, j) for i in range(n_variables) for j in range(i, n_variables)]
    points = []
    for i, j in pairs:
        for si, sj in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            point = np.zeros(n_variables)
            point[i] += si * h
            point[j] += sj * h
            points.append(point)

    values = _wilson_action_batch(np.array(points).reshape(-1, 2, 2, 2, 3, 3), theta)
    values = values.reshape(len(pairs), 4)
    hessian = np.zeros((n_variables, n_variables))
    for row, (i, j) in enumerate(pairs):
        hessian[i, j] = hessian[j, i] = (
            values[row, 0] - values[row, 1] - values[row, 2] + values[row, 3]
        ) / (4 * h * h)
    return hessian


def _maxwell_reference_hessian() -> np.ndarray:
    def link_id(site: tuple[int, int, int], mu: int) -> int:
        return ((site[0] * 2 + site[1]) * 2 + site[2]) * 3 + mu

    rows = []
    for site in product(range(2), repeat=3):
        site_array = np.array(site)
        for mu in range(3):
            for nu in range(mu + 1, 3):
                row = np.zeros(24)
                site_plus_mu = tuple((site_array + np.eye(3, dtype=int)[mu]) % 2)
                site_plus_nu = tuple((site_array + np.eye(3, dtype=int)[nu]) % 2)
                row[link_id(site, mu)] += 1
                row[link_id(site_plus_mu, nu)] += 1
                row[link_id(site_plus_nu, mu)] -= 1
                row[link_id(site, nu)] -= 1
                rows.append(row)

    dmat = np.array(rows)
    maxwell = dmat.T @ dmat
    return np.kron(maxwell, np.eye(3)) / 2.0


def _su_roots(n_colors: int) -> np.ndarray:
    projector = np.eye(n_colors) - np.ones((n_colors, n_colors)) / n_colors
    q_matrix, _ = np.linalg.qr(projector[:, : n_colors - 1])
    roots = []
    for i in range(n_colors):
        for j in range(n_colors):
            if i != j:
                roots.append(q_matrix.T @ (np.eye(n_colors)[i] - np.eye(n_colors)[j]))
    return np.array(roots)


def _spatial_momenta(size: int) -> np.ndarray:
    momenta = np.array(list(product(range(size), repeat=3)))
    return momenta[1:]


def _born_oppenheimer_potential(
    theta: np.ndarray, roots: np.ndarray, size: int, version: str
) -> float:
    momenta = _spatial_momenta(size)
    khat_squared = np.sum(4 * np.sin(np.pi * momenta / size) ** 2, axis=1)
    total = 0.0
    for root in roots:
        phi = theta @ root / 2.0
        if version == "literal":
            nu = np.sum(
                4 * np.sin((np.pi * momenta + phi[None, :]) / size) ** 2, axis=1
            )
        else:
            nu = khat_squared + np.sum(4 * np.sin(phi) ** 2)
        total += np.sum(np.sqrt(nu) - np.sqrt(khat_squared))
    return 0.5 * float(total)


def _finite_difference_hessian(function, n_variables: int, h: float = 1e-4) -> np.ndarray:
    hessian = np.zeros((n_variables, n_variables))
    for i in range(n_variables):
        for j in range(i, n_variables):
            ei = np.zeros(n_variables)
            ej = np.zeros(n_variables)
            ei[i] = h
            ej[j] = h
            hessian[i, j] = hessian[j, i] = (
                function(ei + ej)
                - function(ei - ej)
                - function(-ei + ej)
                + function(-ei - ej)
            ) / (4 * h * h)
    return hessian


def _born_oppenheimer_diagnostic_rows() -> list[dict[str, object]]:
    rows = []
    for n_colors, size in ((2, 4), (2, 8), (3, 4)):
        roots = _su_roots(n_colors)
        rank = n_colors - 1
        n_variables = 3 * rank
        momenta = _spatial_momenta(size)
        s1 = float(
            np.sum(np.sum(4 * np.sin(np.pi * momenta / size) ** 2, axis=1) ** -0.5)
        )
        proof_hessian = _finite_difference_hessian(
            lambda values: _born_oppenheimer_potential(
                values.reshape(3, rank), roots, size, "proof"
            ),
            n_variables,
        )
        literal_hessian = _finite_difference_hessian(
            lambda values: _born_oppenheimer_potential(
                values.reshape(3, rank), roots, size, "literal"
            ),
            n_variables,
        )
        proof_deviation = float(
            np.abs(proof_hessian - n_colors * s1 * np.eye(n_variables)).max()
            / (n_colors * s1)
        )
        rows.append(
            {
                "Nc": n_colors,
                "L": size,
                "rank": rank,
                "variables": n_variables,
                "S1": _rounded_float(s1),
                "proof_hessian_diag_over_S1": _rounded_float(proof_hessian[0, 0] / s1, 4),
                "proof_expected_diag_over_S1": float(n_colors),
                "proof_max_relative_deviation_from_Nc_S1_identity": _rounded_float(
                    proof_deviation, 4
                ),
                "literal_hessian_diag": _rounded_float(literal_hessian[0, 0], 4),
                "literal_max_eigenvalue": _rounded_float(
                    float(np.linalg.eigvalsh(literal_hessian).max()), 4
                ),
            }
        )
    return rows


def _born_oppenheimer_grid_scan() -> dict[str, object]:
    roots = _su_roots(2)
    size = 4
    grid = np.linspace(-np.pi * np.sqrt(2.0), np.pi * np.sqrt(2.0), 15)
    coroot_lattice = np.array([-np.pi * np.sqrt(2.0), 0.0, np.pi * np.sqrt(2.0)])
    proof_min_off_lattice = np.inf
    literal_min = np.inf
    literal_argmin = None

    for t1 in grid:
        for t2 in grid:
            for t3 in grid:
                theta = np.array([[t1], [t2], [t3]])
                proof_value = _born_oppenheimer_potential(theta, roots, size, "proof")
                literal_value = _born_oppenheimer_potential(theta, roots, size, "literal")
                off_lattice = max(
                    min(abs(t - lattice_point) for lattice_point in coroot_lattice)
                    for t in (t1, t2, t3)
                )
                if off_lattice > 1e-6:
                    proof_min_off_lattice = min(proof_min_off_lattice, proof_value)
                if literal_value < literal_min - 1e-10:
                    literal_min = literal_value
                    literal_argmin = (t1, t2, t3)

    assert literal_argmin is not None
    return {
        "case": "SU(2), L=4, grid 15^3",
        "grid_min": _rounded_float(float(grid[0])),
        "grid_max": _rounded_float(float(grid[-1])),
        "proof_min_off_coroot_lattice": _rounded_float(float(proof_min_off_lattice)),
        "literal_min": _rounded_float(float(literal_min)),
        "literal_argmin": [_rounded_float(value) for value in literal_argmin],
    }


def _transfer_matrix_kernel(
    grid_size: int, beta: float, pinning: float
) -> tuple[np.ndarray, np.ndarray]:
    theta = 2.0 * np.pi * np.arange(grid_size) / grid_size
    delta = theta[:, None] - theta[None, :]
    onsite = 1.0 - np.cos(theta)
    kernel = np.exp(
        beta * np.cos(delta) - 0.5 * pinning * (onsite[:, None] + onsite[None, :])
    )
    return theta, kernel


def _finite_window_transfer_matrix_diagnostic() -> dict[str, object]:
    beta = 0.85
    pinning = 0.2
    rows = []
    previous_gap = None
    gap_changes = []
    for grid_size in (8, 16, 32):
        theta, kernel = _transfer_matrix_kernel(grid_size, beta, pinning)
        eigenvalues = np.linalg.eigvalsh(kernel)
        leading = float(eigenvalues[-1])
        second = float(eigenvalues[-2])
        normalized_gap = 1.0 - second / leading

        wrapped_theta = (theta + np.pi) % (2.0 * np.pi) - np.pi
        window_mask = np.abs(wrapped_theta) <= np.pi / 2.0 + 1e-12
        window_kernel = kernel[np.ix_(window_mask, window_mask)]
        window_eigenvalues = np.linalg.eigvalsh(window_kernel)
        window_leading = float(window_eigenvalues[-1])
        window_second = float(window_eigenvalues[-2])

        gap_change = None
        if previous_gap is not None:
            gap_change = abs(normalized_gap - previous_gap)
            gap_changes.append(gap_change)
        previous_gap = normalized_gap

        rows.append(
            {
                "grid_size": grid_size,
                "window_points": int(np.sum(window_mask)),
                "leading_eigenvalue": _rounded_float(leading),
                "second_eigenvalue": _rounded_float(second),
                "normalized_gap": _rounded_float(normalized_gap),
                "gap_change_from_previous_grid": (
                    None if gap_change is None else _rounded_float(gap_change)
                ),
                "window_leading_eigenvalue": _rounded_float(window_leading),
                "window_normalized_gap": _rounded_float(
                    1.0 - window_second / window_leading
                ),
                "symmetry_error": _rounded_float(float(np.abs(kernel - kernel.T).max())),
            }
        )

    return {
        "reference": "synthetic finite-window transfer-matrix check",
        "model": "one compact rotor with cosine coupling and cosine pinning",
        "parameters": {
            "beta": beta,
            "pinning": pinning,
            "window": "|theta| <= pi/2",
        },
        "rows": rows,
        "max_gap_change_after_doubling": _rounded_float(max(gap_changes)),
        "consumption_limit": (
            "Synthetic finite-matrix sanity check only; it is not a transfer "
            "operator construction for the conditional paper."
        ),
    }


def _rounded_eigenvalues(values: np.ndarray) -> list[float]:
    nonzero = values[np.abs(values) > 1e-3]
    return [float(value) for value in sorted(set(np.round(nonzero, 5)))]


def _rounded_float(value: float, digits: int = 12) -> float:
    return float(round(float(value), digits))


def build_report() -> dict[str, object]:
    hessian_zero = _wilson_hessian((0.0, 0.0, 0.0))
    maxwell_reference = _maxwell_reference_hessian()
    eig_zero = np.linalg.eigvalsh(hessian_zero)

    toron_direction = np.zeros((2, 2, 2, 3, 3))
    toron_direction[:, :, :, 0, 0] = 1.0
    toron_direction[:, :, :, 1, 1] = 1.0
    f_t = float(_wilson_action_batch((0.02 * toron_direction)[None], (0.0, 0.0, 0.0))[0])
    f_2t = float(_wilson_action_batch((0.04 * toron_direction)[None], (0.0, 0.0, 0.0))[0])

    generic_theta = (0.53, 0.91, 0.36)
    hessian_generic = _wilson_hessian(generic_theta)
    eig_generic = np.linalg.eigvalsh(hessian_generic)
    positive_generic = eig_generic[np.abs(eig_generic) > 1e-3]

    report = {
        "schema_version": 1,
        "source": "2602.0032 conditional Witten-lattice diagnostics",
        "honesty": (
            "Numerical sidecar diagnostics only. These checks do not prove any "
            "hypothesis, source construction, continuum statement, or mass-gap claim."
        ),
        "diagnostics": {
            "wilson_hessian_su2_2x2x2": {
                "lattice": "2^3 spatial periodic",
                "variables": 72,
                "theta_zero": {
                    "theta": [0.0, 0.0, 0.0],
                    "kernel_dimension": int(np.sum(np.abs(eig_zero) < 1e-3)),
                    "expected_kernel_dimension": 30,
                    "flat_tangent_dimension_reference": 24,
                    "maxwell_metric_factor": "1/Nc for Nc=2",
                    "max_abs_deviation_from_maxwell_reference": _rounded_float(
                        float(np.abs(hessian_zero - maxwell_reference).max())
                    ),
                    "nonzero_eigenvalues_unique": _rounded_eigenvalues(eig_zero),
                },
                "quartic_toron_ratio": {
                    "t": 0.02,
                    "action_at_t": _rounded_float(f_t),
                    "action_at_2t": _rounded_float(f_2t),
                    "ratio": _rounded_float(f_2t / f_t),
                    "expected_near": 16.0,
                },
                "generic_theta": {
                    "theta": list(generic_theta),
                    "kernel_dimension": int(np.sum(np.abs(eig_generic) < 1e-3)),
                    "expected_kernel_dimension": 26,
                    "min_positive_eigenvalue": _rounded_float(float(positive_generic.min())),
                },
            },
            "born_oppenheimer_vbo_lemma_5_2": {
                "reference": "verify_2602_0032.py Lemma 5.2 diagnostic",
                "versions": {
                    "proof": "omega^2 = khat^2 + m_a(theta)^2",
                    "literal": "paper-v1 literal equations (2)+(3) inside sin^2",
                },
                "hessian_rows": _born_oppenheimer_diagnostic_rows(),
                "grid_scan": _born_oppenheimer_grid_scan(),
                "consumption_limit": (
                    "Finite-dimensional diagnostic for the conditional paper only; "
                    "it records a proof-formula versus literal-formula mismatch."
                ),
            },
            "finite_window_transfer_matrix_synthetic": (
                _finite_window_transfer_matrix_diagnostic()
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
        default=Path("data/processed/witten_2602_0032_diagnostics.json"),
    )
    args = parser.parse_args(argv)
    write_report(build_report(), args.output)
    print(f"diagnostics written: {args.output}")


if __name__ == "__main__":
    main()
