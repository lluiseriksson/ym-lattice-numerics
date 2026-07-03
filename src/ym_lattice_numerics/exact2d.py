"""Exact two-dimensional SU(2) Wilson-action benchmarks with certified enclosures.

In two dimensions the Wilson-action plaquettes decouple and the theory is
exactly soluble: the mean plaquette is the Bessel ratio

``<1/2 Re Tr U_p> = I_2(beta) / I_1(beta)``

and the (infinite-volume) string tension is exact,

``sigma(beta) = -log(I_2(beta) / I_1(beta))``.

This module computes certified interval enclosures of these quantities using
the truncated modified-Bessel power series with an explicit geometric tail
bound, entirely in outward-rounded decimal interval arithmetic.  It is the
numerical twin of the ``lean-2d-yang-mills`` satellite: the same exactly
soluble sandbox, from the empirical side.

Finite-volume note: on a finite 2D torus with V plaquettes the mean
plaquette differs from the Bessel ratio by terms of relative size
``O((I_2/I_1)^(V-1))``, which is far below statistical errors for the
lattice sizes used in the tests.

References: Migdal (1975, Sov. Phys. JETP 42, 413-418); Creutz (1983),
"Quarks, Gluons and Lattices", Chapter 9 (two-dimensional exactness).
"""

from __future__ import annotations

import math
from decimal import Decimal

from .intervals import Interval, dec, sum_intervals


def _factorial(n: int) -> int:
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


def bessel_i_interval(nu: int, beta: object, terms: int = 40) -> Interval:
    """Certified enclosure of the modified Bessel function ``I_nu(beta)``.

    Uses the power series ``I_nu(x) = sum_m (x/2)^(2m+nu) / (m! (m+nu)!)``
    truncated after ``terms`` terms, plus a rigorous geometric tail bound.
    Requires ``beta >= 0`` and enough terms for the tail ratio to drop below
    one; raises ``ValueError`` otherwise.
    """

    if nu < 0:
        raise ValueError("nu must be a nonnegative integer")
    if terms < 1:
        raise ValueError("need at least one series term")
    b = Interval.parse(beta)
    if b.lo < 0:
        raise ValueError("beta must be nonnegative")

    half = b * Interval(dec("0.5"), dec("0.5"))
    half_sq = half * half

    partial_terms = []
    term = half.pow_int(nu) / Interval.point(_factorial(nu))
    partial_terms.append(term)
    for m in range(1, terms):
        term = term * half_sq / Interval.point(m * (m + nu))
        partial_terms.append(term)
    partial = sum_intervals(partial_terms)

    # Tail bound: for m >= terms the term ratio is at most
    # (beta_hi/2)^2 / (terms * (terms + nu)) =: q, so the tail is bounded by
    # last_term_hi * q / (1 - q) provided q < 1.
    m0 = terms
    q = (half_sq / Interval.point(m0 * (m0 + nu))).hi
    if q >= 1:
        raise ValueError(
            f"series truncation too short for beta up to {b.hi}: "
            f"tail ratio {q} >= 1; increase `terms`"
        )
    last_hi = max(term.hi, Decimal(0))
    tail_hi = (Interval(last_hi, last_hi) * Interval(q, q)
               / Interval(Decimal(1) - q, Decimal(1) - q)).hi
    tail = Interval(Decimal(0), max(tail_hi, Decimal(0)))
    return partial + tail


def plaquette_exact_interval(beta: object, terms: int = 40) -> Interval:
    """Certified enclosure of the exact 2D mean plaquette ``I_2/I_1``."""

    b = Interval.parse(beta)
    if b.lo <= 0:
        raise ValueError("beta must be strictly positive")
    return bessel_i_interval(2, b, terms) / bessel_i_interval(1, b, terms)


def string_tension_exact_interval(beta: object, terms: int = 40) -> Interval:
    """Certified enclosure of the exact 2D string tension
    ``sigma = -log(I_2/I_1)`` (lattice units, per unit area)."""

    ratio = plaquette_exact_interval(beta, terms)
    minus_log = Interval.point(0) - ratio.ln()
    return minus_log


def bessel_i(nu: int, beta: float, terms: int = 40) -> float:
    """Float midpoint of the certified Bessel enclosure."""

    iv = bessel_i_interval(nu, beta, terms)
    return float((iv.lo + iv.hi) / 2)


def plaquette_exact(beta: float, terms: int = 40) -> float:
    """Float midpoint of the exact 2D mean plaquette."""

    iv = plaquette_exact_interval(beta, terms)
    return float((iv.lo + iv.hi) / 2)


def string_tension_exact(beta: float, terms: int = 40) -> float:
    """Float midpoint of the exact 2D string tension."""

    iv = string_tension_exact_interval(beta, terms)
    return float((iv.lo + iv.hi) / 2)


def strong_coupling_plaquette(beta: float, terms: int = 40) -> float:
    """Leading strong-coupling estimate of the mean plaquette in any
    dimension: the single-plaquette (2D-exact) value ``I_2/I_1``, correct to
    ``O(beta^5)`` corrections from multi-plaquette diagrams."""

    return plaquette_exact(beta, terms)
