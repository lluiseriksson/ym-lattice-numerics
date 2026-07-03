"""Statistical analysis: jackknife errors, binning, and effective masses.

These estimators feed milestones M1 (string tension with errors) and M2
(effective masses from temporal correlators).  Everything here is exactly
testable on synthetic data.

References: Berg (2004), "Markov Chain Monte Carlo Simulations and Their
Statistical Analysis", Chapter 2 (jackknife); Montvay-Muenster (1994),
Section 7.3 (Creutz ratios and effective masses).
"""

from __future__ import annotations

import math
from typing import Callable, Sequence

import numpy as np


def jackknife(values: Sequence[float],
              estimator: Callable[[np.ndarray], float] | None = None) -> tuple[float, float]:
    """Jackknife mean and error of an estimator over samples.

    Returns ``(estimate, error)`` where ``estimate`` is the estimator on the
    full sample and ``error`` the jackknife standard error.  With the default
    mean estimator the jackknife error equals the standard error of the mean
    exactly.
    """

    data = np.asarray(values, dtype=np.float64)
    n = data.size
    if n < 2:
        raise ValueError("jackknife needs at least two samples")
    if estimator is None:
        estimator = lambda x: float(np.mean(x))

    full = estimator(data)
    leave_one_out = np.empty(n, dtype=np.float64)
    for i in range(n):
        leave_one_out[i] = estimator(np.delete(data, i))
    center = float(np.mean(leave_one_out))
    var = (n - 1) / n * float(np.sum((leave_one_out - center) ** 2))
    return full, math.sqrt(var)


def binned_series(values: Sequence[float], bin_size: int) -> np.ndarray:
    """Average consecutive bins; incomplete trailing bins are dropped."""

    data = np.asarray(values, dtype=np.float64)
    if bin_size < 1:
        raise ValueError("bin_size must be positive")
    nbins = data.size // bin_size
    if nbins < 1:
        raise ValueError("not enough samples for one bin")
    return data[: nbins * bin_size].reshape(nbins, bin_size).mean(axis=1)


def binned_error(values: Sequence[float], bin_size: int) -> float:
    """Standard error of the mean computed on binned samples (autocorrelation
    mitigation)."""

    bins = binned_series(values, bin_size)
    if bins.size < 2:
        raise ValueError("need at least two bins")
    return float(np.std(bins, ddof=1) / math.sqrt(bins.size))


def creutz_string_tension(w11: Sequence[float], w12: Sequence[float],
                          w22: Sequence[float]) -> tuple[float, float]:
    """String tension from the 2x2 Creutz ratio
    ``chi(2,2) = -log(W22 * W11 / W12^2)`` with jackknife error over paired
    samples."""

    a = np.asarray(w11, dtype=np.float64)
    b = np.asarray(w12, dtype=np.float64)
    c = np.asarray(w22, dtype=np.float64)
    if not (a.size == b.size == c.size):
        raise ValueError("paired samples required")

    stacked = np.arange(a.size)

    def estimator(idx: np.ndarray) -> float:
        ii = idx.astype(int)
        return -math.log(np.mean(c[ii]) * np.mean(a[ii]) / np.mean(b[ii]) ** 2)

    return jackknife(stacked, estimator)


def effective_mass(correlator: Sequence[float]) -> list[float]:
    """Effective masses ``m_eff(t) = log(C(t) / C(t+1))`` for a positive,
    decaying correlator.  On a pure exponential ``C(t) = A e^(-m t)`` every
    entry equals ``m`` exactly (up to rounding)."""

    data = np.asarray(correlator, dtype=np.float64)
    if np.any(data <= 0):
        raise ValueError("correlator entries must be positive")
    return [float(math.log(data[t] / data[t + 1])) for t in range(data.size - 1)]
