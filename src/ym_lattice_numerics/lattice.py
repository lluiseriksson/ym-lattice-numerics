"""Reference SU(2) lattice gauge kernels for Wilson action simulations."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterator, Tuple

import numpy as np

from . import su2

Site = Tuple[int, ...]


@dataclass(frozen=True)
class LatticeSpec:
    """Hypercubic lattice specification."""

    length: int
    ndim: int = 4

    def shape(self) -> Tuple[int, ...]:
        return (self.length,) * self.ndim


def cold_start(spec: LatticeSpec) -> np.ndarray:
    """Create a cold-start gauge field with every link equal to identity."""

    links = np.zeros(spec.shape() + (spec.ndim, 4), dtype=np.float64)
    links[..., 0] = 1.0
    return links


def hot_start(spec: LatticeSpec, rng: np.random.Generator) -> np.ndarray:
    """Create a hot-start gauge field with independent Haar SU(2) links."""

    return su2.random(rng, spec.shape() + (spec.ndim,))


def iter_sites(spec: LatticeSpec) -> Iterator[Site]:
    return np.ndindex(spec.shape())


def shift(site: Site, direction: int, step: int, length: int) -> Site:
    out = list(site)
    out[direction] = (out[direction] + step) % length
    return tuple(out)


def plaquette(links: np.ndarray, site: Site, mu: int, nu: int) -> np.ndarray:
    """Return the oriented plaquette quaternion at ``site`` in the ``mu,nu`` plane."""

    length = links.shape[0]
    x_mu = shift(site, mu, 1, length)
    x_nu = shift(site, nu, 1, length)
    return su2.mul(
        su2.mul(links[site + (mu,)], links[x_mu + (nu,)]),
        su2.mul(su2.conj(links[x_nu + (mu,)]), su2.conj(links[site + (nu,)])),
    )


def mean_plaquette(links: np.ndarray) -> float:
    """Average ``1/2 Re Tr`` over all oriented positive plaquettes."""

    ndim = links.shape[-2]
    spec = LatticeSpec(length=links.shape[0], ndim=ndim)
    total = 0.0
    count = 0
    for site in iter_sites(spec):
        for mu, nu in combinations(range(ndim), 2):
            total += float(su2.real_trace_half(plaquette(links, site, mu, nu)))
            count += 1
    return total / count


def staple(links: np.ndarray, site: Site, mu: int) -> np.ndarray:
    """Sum the forward and backward staples touching one link."""

    length = links.shape[0]
    ndim = links.shape[-2]
    total = np.zeros(4, dtype=np.float64)
    x_mu = shift(site, mu, 1, length)

    for nu in range(ndim):
        if nu == mu:
            continue

        x_nu = shift(site, nu, 1, length)
        forward = su2.mul(
            su2.mul(links[x_mu + (nu,)], su2.conj(links[x_nu + (mu,)])),
            su2.conj(links[site + (nu,)]),
        )

        x_minus_nu = shift(site, nu, -1, length)
        x_mu_minus_nu = shift(x_mu, nu, -1, length)
        backward = su2.mul(
            su2.mul(su2.conj(links[x_mu_minus_nu + (nu,)]), su2.conj(links[x_minus_nu + (mu,)])),
            links[x_minus_nu + (nu,)],
        )
        total += forward + backward

    return total


def heatbath_sweep(links: np.ndarray, beta: float, rng: np.random.Generator) -> None:
    """Perform one in-place SU(2) heat-bath sweep."""

    spec = LatticeSpec(length=links.shape[0], ndim=links.shape[-2])
    for site in iter_sites(spec):
        for mu in range(spec.ndim):
            st = staple(links, site, mu)
            norm = float(np.linalg.norm(st))
            if norm <= 1e-14:
                links[site + (mu,)] = su2.random(rng)
                continue
            v = st / norm
            x = su2.sample_heatbath(beta * norm, rng)
            links[site + (mu,)] = su2.normalize(su2.mul(x, su2.conj(v)))


def overrelaxation_sweep(links: np.ndarray) -> None:
    """Perform one in-place microcanonical overrelaxation sweep."""

    spec = LatticeSpec(length=links.shape[0], ndim=links.shape[-2])
    for site in iter_sites(spec):
        for mu in range(spec.ndim):
            st = staple(links, site, mu)
            norm = float(np.linalg.norm(st))
            if norm <= 1e-14:
                continue
            v_inv = su2.conj(st / norm)
            old = links[site + (mu,)]
            links[site + (mu,)] = su2.normalize(su2.mul(su2.mul(v_inv, su2.conj(old)), v_inv))
