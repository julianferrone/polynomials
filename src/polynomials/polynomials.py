from __future__ import annotations
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction


class Polynomial:
    coeffs: defaultdict[int, Fractional]

    # ------------
    # Constructors
    # ------------

    def __init__(self, coeffs: dict[int, int | Fraction]) -> Polynomial:
        self.coeffs = defaultdict(
            int,
            {power: Fraction(coeff) for power, coeff in coeffs.items() if coeff != 0},
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

    # ------------------
    # Printing to String
    # ------------------

    def __repr__(self):
        return f"Polynomial({self.coeffs!r})"

    # ----------
    # Properties
    # ----------

    @property
    def is_zero(self) -> bool:
        return False if self.coeffs else True

    @property
    def degree(self) -> int:
        # Convention for empty polynomials is that they have a degree of
        # negative infinity, but this would require returning a float.
        if self.is_zero:
            return -1
        return max(self.coeffs.keys())

    @property
    def leading_term(self) -> Polynomial:
        term = max(self.coeffs.items(), default=(0, 0), key=lambda pair: pair[0])
        return Polynomial(dict(term))

    # --------------------
    # Algebraic Operations
    # --------------------

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
        coeffs = defaultdict(Fraction)
        for power, coeff in self.coeffs.items():
            coeffs[power] += coeff
        for power, coeff in other.coeffs.items():
            coeffs[power] += coeff
        return Polynomial(coeffs)

    def __neg__(self):
        coeffs = defaultdict(Fraction)
        for power, coeff in self.coeffs.items():
            coeffs[power] -= coeff
        return Polynomial(coeffs)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        coeffs = defaultdict(Fraction)
        for power_a, coeff_a in self.coeffs.items():
            for power_b, coeff_b in other.coeffs.items():
                coeffs[power_a + power_b] += coeff_a * coeff_b
        return Polynomial(coeffs)
