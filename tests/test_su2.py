from __future__ import annotations

import numpy as np

from ym_lattice_numerics import su2


def test_identity_and_inverse() -> None:
    rng = np.random.default_rng(123)
    q = su2.random(rng)
    np.testing.assert_allclose(su2.mul(su2.IDENTITY, q), q, atol=1e-12)
    np.testing.assert_allclose(su2.mul(q, su2.conj(q)), su2.IDENTITY, atol=1e-12)


def test_heatbath_samples_are_unit_quaternions() -> None:
    rng = np.random.default_rng(456)
    for alpha in [0.0, 0.5, 3.0]:
        q = su2.sample_heatbath(alpha, rng)
        np.testing.assert_allclose(np.linalg.norm(q), 1.0, atol=1e-12)
