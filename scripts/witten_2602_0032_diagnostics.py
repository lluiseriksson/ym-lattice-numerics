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
            }
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
