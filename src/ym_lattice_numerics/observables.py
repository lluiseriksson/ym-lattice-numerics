"""Gauge-invariant observables used by the numerical sidecar."""

from __future__ import annotations

import math
from itertools import product
from typing import Iterable, Tuple

import numpy as np

from . import su2
from .lattice import LatticeSpec, Site, iter_sites, shift

Step = Tuple[int, int]


def path_product(links: np.ndarray, site: Site, steps: Iterable[Step]) -> np.ndarray:
    """Transport around a path encoded as ``(direction, sign)`` steps."""

    length = links.shape[0]
    pos = site
    acc = su2.IDENTITY
    for direction, sign in steps:
        if sign == 1:
            acc = su2.mul(acc, links[pos + (direction,)])
            pos = shift(pos, direction, 1, length)
        elif sign == -1:
            pos = shift(pos, direction, -1, length)
            acc = su2.mul(acc, su2.conj(links[pos + (direction,)]))
        else:
            raise ValueError("path step sign must be +1 or -1")
    return acc


def rectangular_loop(links: np.ndarray, site: Site, mu: int, nu: int, r: int, t: int) -> np.ndarray:
    """Return a rectangular Wilson loop quaternion."""

    if r <= 0 or t <= 0:
        raise ValueError("loop extents must be positive")
    steps = [(mu, 1)] * r + [(nu, 1)] * t + [(mu, -1)] * r + [(nu, -1)] * t
    return path_product(links, site, steps)


def mean_wilson_loop(links: np.ndarray, r: int, t: int) -> float:
    """Average rectangular Wilson loop over positions and oriented coordinate planes."""

    ndim = links.shape[-2]
    spec = LatticeSpec(length=links.shape[0], ndim=ndim)
    total = 0.0
    count = 0
    for site in iter_sites(spec):
        for mu, nu in product(range(ndim), repeat=2):
            if mu == nu:
                continue
            total += float(su2.real_trace_half(rectangular_loop(links, site, mu, nu, r, t)))
            count += 1
    return total / count


def creutz_ratio(w_rt: float, w_r1_t: float, w_r_t1: float, w_r1_t1: float) -> float:
    """Compute ``chi(R,T) = -log(W(R,T) W(R-1,T-1)/(W(R-1,T) W(R,T-1)))``."""

    numerator = w_rt * w_r1_t1
    denominator = w_r1_t * w_r_t1
    if numerator <= 0.0 or denominator <= 0.0:
        return math.nan
    return -math.log(numerator / denominator)


def creutz_ratio_from_links(links: np.ndarray, r: int, t: int) -> float:
    """Compute a Creutz ratio directly from lattice links."""

    if r <= 1 or t <= 1:
        raise ValueError("Creutz ratios require r,t >= 2")
    return creutz_ratio(
        mean_wilson_loop(links, r, t),
        mean_wilson_loop(links, r - 1, t),
        mean_wilson_loop(links, r, t - 1),
        mean_wilson_loop(links, r - 1, t - 1),
    )
