from __future__ import annotations
from collections import defaultdict


class Polynomial:
    coeffs: defaultdict[int, int]

    def __init__(self, coeffs: dict[int, int]) -> Polynomial:
        self.coeffs = defaultdict(
            int, {power: coeff for power, coeff in coeffs.items() if coeff != 0}
        )

    @classmethod
    def from_coeffs(cls, *args) -> Polynomial:
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        # We need to iterate in reverse order so that users can
        # define the polynomials in standard form (i.e. highest
        # powers first:
        #
        # from_coeffs(1, -2, 3) == x^2 - 2x + 3
        coeffs = dict(enumerate(reversed(args)))
        return cls(coeffs)

    @classmethod
    def zero(cls) -> Polynomial:
        return cls.from_coeffs(0)

    @classmethod
    def one(cls) -> Polynomial:
        return cls.from_coeffs(1)

    def __repr__(self):
        return f"Polynomial({self.coeffs!r})"

    def __eq__(self, other):
        return self.coeffs == other.coeffs

    def __add__(self, other):
        # Note: it would be great to just implement this with something like
        # a Counter, and then add them together:
        # `coeffs = self.coeffs + power.coeffs`
        #
        # However, these operations on Counters exclude outputs with negative
        # counts. As per the docs on Counter objects:
        #
        # > Several mathematical operations are provided for combining Counter
        # > objects to produce multisets (counters that have counts greater
        # > than zero). Addition and subtraction combine counters by adding or
        # > subtracting the counts of corresponding elements.
        # > ...
        # > Each operation can accept inputs with signed counts, but the output
        # > will exclude results with counts of zero or below.
        coeffs = defaultdict(int)
        for power, coeff in self.coeffs.items():
            coeffs[power] += coeff
        for power, coeff in other.coeffs.items():
            coeffs[power] += coeff
        return Polynomial(coeffs)

    def __neg__(self):
        coeffs = defaultdict(int)
        for power, coeff in self.coeffs.items():
            coeffs[power] -= coeff
        return Polynomial(coeffs)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        coeffs = defaultdict(int)
        for power_a, coeff_a in self.coeffs.items():
            for power_b, coeff_b in other.coeffs.items():
                coeffs[power_a + power_b] += coeff_a * coeff_b
        return Polynomial(coeffs)
