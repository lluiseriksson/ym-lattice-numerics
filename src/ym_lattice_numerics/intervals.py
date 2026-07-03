"""Small outward-rounded decimal interval arithmetic for M3 checks."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from typing import Callable, Iterable

PRECISION = 80


def dec(value: object) -> Decimal:
    return Decimal(str(value))


def directed(fn: Callable[[], Decimal], rounding: str) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PRECISION
        ctx.rounding = rounding
        return +fn()


@dataclass(frozen=True)
class Interval:
    """Closed decimal interval with outward-rounded arithmetic."""

    lo: Decimal
    hi: Decimal

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError(f"invalid interval [{self.lo}, {self.hi}]")

    @classmethod
    def point(cls, value: object) -> "Interval":
        x = dec(value)
        return cls(x, x)

    @classmethod
    def parse(cls, value: object) -> "Interval":
        if isinstance(value, Interval):
            return value
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return cls(dec(value[0]), dec(value[1]))
        return cls.point(value)

    def __add__(self, other: object) -> "Interval":
        rhs = Interval.parse(other)
        return Interval(
            directed(lambda: self.lo + rhs.lo, ROUND_FLOOR),
            directed(lambda: self.hi + rhs.hi, ROUND_CEILING),
        )

    def __radd__(self, other: object) -> "Interval":
        return self + other

    def __sub__(self, other: object) -> "Interval":
        rhs = Interval.parse(other)
        return Interval(
            directed(lambda: self.lo - rhs.hi, ROUND_FLOOR),
            directed(lambda: self.hi - rhs.lo, ROUND_CEILING),
        )

    def __rsub__(self, other: object) -> "Interval":
        return Interval.parse(other) - self

    def __mul__(self, other: object) -> "Interval":
        rhs = Interval.parse(other)
        pairs = [
            (self.lo, rhs.lo),
            (self.lo, rhs.hi),
            (self.hi, rhs.lo),
            (self.hi, rhs.hi),
        ]
        lows = [directed(lambda a=a, b=b: a * b, ROUND_FLOOR) for a, b in pairs]
        highs = [directed(lambda a=a, b=b: a * b, ROUND_CEILING) for a, b in pairs]
        return Interval(min(lows), max(highs))

    def __rmul__(self, other: object) -> "Interval":
        return self * other

    def reciprocal(self) -> "Interval":
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError("interval contains zero")
        vals_lo = [
            directed(lambda: Decimal(1) / self.lo, ROUND_FLOOR),
            directed(lambda: Decimal(1) / self.hi, ROUND_FLOOR),
        ]
        vals_hi = [
            directed(lambda: Decimal(1) / self.lo, ROUND_CEILING),
            directed(lambda: Decimal(1) / self.hi, ROUND_CEILING),
        ]
        return Interval(min(vals_lo), max(vals_hi))

    def __truediv__(self, other: object) -> "Interval":
        return self * Interval.parse(other).reciprocal()

    def __rtruediv__(self, other: object) -> "Interval":
        return Interval.parse(other) / self

    def pow_int(self, exponent: int) -> "Interval":
        if exponent < 0:
            return self.reciprocal().pow_int(-exponent)
        result = Interval.point(1)
        for _ in range(exponent):
            result *= self
        return result

    def to_json(self) -> list[str]:
        return [str(self.lo), str(self.hi)]


def sum_intervals(values: Iterable[Interval]) -> Interval:
    total = Interval.point(0)
    for value in values:
        total += value
    return total


def certify_less(lhs: Interval, rhs: Interval) -> str:
    """Return ``pass``, ``fail``, or ``unknown`` for interval comparison ``lhs < rhs``."""

    if lhs.hi < rhs.lo:
        return "pass"
    if lhs.lo >= rhs.hi:
        return "fail"
    return "unknown"
