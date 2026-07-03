"""SU(2) operations represented by unit quaternions.

The quaternion ``(a0, a1, a2, a3)`` represents

``[[a0 + i a3, a2 + i a1], [-a2 + i a1, a0 - i a3]]``.

With this convention, ``1/2 Re Tr(U) = a0``.
"""

from __future__ import annotations

import math
from typing import Tuple

import numpy as np

Array = np.ndarray
IDENTITY = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)


def normalize(q: Array, eps: float = 1e-14) -> Array:
    """Normalize one quaternion or an array of quaternions along the last axis."""

    q = np.asarray(q, dtype=np.float64)
    norm = np.linalg.norm(q, axis=-1, keepdims=True)
    if np.any(norm < eps):
        raise ValueError("cannot normalize a near-zero quaternion")
    return q / norm


def conj(q: Array) -> Array:
    """Quaternion conjugation, equal to SU(2) inverse for unit quaternions."""

    q = np.asarray(q, dtype=np.float64)
    out = q.copy()
    out[..., 1:] *= -1.0
    return out


def mul(a: Array, b: Array) -> Array:
    """Quaternion product with NumPy broadcasting."""

    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a0, a1, a2, a3 = np.moveaxis(a, -1, 0)
    b0, b1, b2, b3 = np.moveaxis(b, -1, 0)
    return np.stack(
        [
            a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3,
            a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
            a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1,
            a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0,
        ],
        axis=-1,
    )


def real_trace_half(q: Array) -> Array:
    """Return ``1/2 Re Tr`` for the represented SU(2) matrix."""

    return np.asarray(q, dtype=np.float64)[..., 0]


def random(rng: np.random.Generator, size: Tuple[int, ...] = ()) -> Array:
    """Draw Haar-distributed SU(2) elements by normalizing Gaussian quaternions."""

    q = rng.normal(size=size + (4,))
    return normalize(q)


def random_unit_vector3(rng: np.random.Generator) -> Array:
    """Draw a random unit vector on S^2."""

    v = rng.normal(size=3)
    n = float(np.linalg.norm(v))
    if n == 0.0:
        return np.array([1.0, 0.0, 0.0], dtype=np.float64)
    return v / n


def _heatbath_log_density(x: float, alpha: float) -> float:
    return 0.5 * math.log(max(0.0, 1.0 - x * x)) + alpha * x


def _heatbath_mode(alpha: float) -> float:
    if alpha <= 1e-14:
        return 0.0
    return (-1.0 + math.sqrt(1.0 + 4.0 * alpha * alpha)) / (2.0 * alpha)


def sample_heatbath(alpha: float, rng: np.random.Generator, max_tries: int = 100_000) -> Array:
    """Sample the SU(2) one-link heat-bath distribution.

    The scalar part has density proportional to
    ``sqrt(1 - x^2) * exp(alpha * x)`` on ``[-1, 1]``; the vector direction is
    uniform on S^2. This simple rejection sampler is intended as a correct
    reference kernel, not the final high-throughput production implementation.
    """

    if alpha < 0:
        raise ValueError("alpha must be nonnegative")
    if alpha <= 1e-14:
        return random(rng)

    x_mode = _heatbath_mode(alpha)
    log_max = _heatbath_log_density(x_mode, alpha)
    for _ in range(max_tries):
        x = float(rng.uniform(-1.0, 1.0))
        log_accept = _heatbath_log_density(x, alpha) - log_max
        if math.log(float(rng.random())) <= log_accept:
            radius = math.sqrt(max(0.0, 1.0 - x * x))
            direction = random_unit_vector3(rng)
            return np.array([x, *(radius * direction)], dtype=np.float64)
    raise RuntimeError("SU(2) heat-bath rejection sampler exceeded max_tries")
