from __future__ import annotations
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from math import ceil


class Polynomial:
    coeffs: defaultdict[int, Fractional]

    # ------------
    # Constructors
    # ------------

    def __init__(self, coeffs: dict[int, int | Fraction]) -> Polynomial:
        self.coeffs = defaultdict(
            Fraction,
            {
                power: Fraction(coeff)
                for power, coeff in coeffs.items()
                if power >= 0 and coeff != 0
            },
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

    # -------------------
    # Getting and Setting
    # -------------------

    def __getitem__(self, power):
        return self.coeffs.get(power, 0)

    def __setitem__(self, power, coeff):
        if coeff == 0 or 0 > power:
            pass
        else:
            self.coeffs[power] = coeff

    def slice(self, start, end):
        coeffs = {
            power: coeff
            for power, coeff in self.coeffs.items()
            if start <= power and power < end
        }
        return Polynomial(coeffs)

    # ------------------
    # Printing to String
    # ------------------

    def __str__(self):
        def term(power, coeff):
            if power == 0:
                return str(coeff)
            else:
                coeff = "" if coeff == 1 else str(coeff)
                power = "" if power == 1 else f"^{power}"
                return f"{coeff}x{power}"
        
        parts = iter(sorted(self.coeffs.items(), reverse=True))

        # As we filter out powers with zero coefficients when constructing a
        # Polynomial, a zero Polynomial will have an empty Counter and so
        # next() will fail with a StopIteration
        try:
            power, coeff = next(parts)
        except StopIteration:
            return "0"

        s = "" if coeff >= 0 else "-"
        s += term(power, abs(coeff))
        for power, coeff in parts:
            sign = " + " if coeff >= 0 else " - "
            s += sign
            s += term(power, abs(coeff))
        return s

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
    def leading_term(self) -> (int, int):
        return max(self.coeffs.items(), default=(0, 0), key=lambda pair: pair[0])

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
        return self.fast_mul(other)

    def fast_mul(self, other):
        # Implements Karatsuba's multiplication on polynomials
        tasks = []
        values = []
        tasks.append(("mul", self, other))
        while tasks:
            task = tasks.pop()
            tag = task[0]
            if tag == "mul":
                p, q = task[1], task[2]
                # Early exit on 0
                if p.is_zero or q.is_zero:
                    values.append(Polynomial.zero())
                    continue
                # Early exit on 1
                if p == Polynomial.one():
                    values.append(q)
                    continue
                if q == Polynomial.one():
                    values.append(p)
                    continue
                # Early exit on -1
                if p == -Polynomial.one():
                    values.append(-q)
                    continue
                if q == -Polynomial.one():
                    values.append(-p)
                    continue

                n = max(p.degree, q.degree)
                if n <= 1:
                    product = p.slow_mul(q)
                    values.append(product)
                    continue

                m = ceil(n / 2)

                p_lower = p.slice(0, m)
                q_lower = q.slice(0, m)

                p_upper = p.slice(m, n + 1).factor_out(m)
                q_upper = q.slice(m, n + 1).factor_out(m)

                p_prime = p_lower + p_upper
                q_prime = q_lower + q_upper

                r1 = ("mul", p_lower, q_lower)
                r2 = ("mul", p_upper, q_upper)
                r3 = ("mul", p_prime, q_prime)

                tasks.append(("combine", m, n))
                tasks.append(r1)
                tasks.append(r2)
                tasks.append(r3)

            elif tag == "combine":
                m, n = task[1], task[2]
                r1 = values.pop()
                r2 = values.pop()
                r3 = values.pop()
                r4 = r3 - r1 - r2

                r = Polynomial.zero()
                for i in range(2 * n + 1):
                    r[i] = r1[i] + r4[i - m] + r2[i - 2 * m]
                values.append(r)
        return values.pop()

    def slow_mul(self, other):
        # n^2 multiplication
        coeffs = defaultdict(Fraction)
        for power_a, coeff_a in self.coeffs.items():
            for power_b, coeff_b in other.coeffs.items():
                coeffs[power_a + power_b] += coeff_a * coeff_b
        return Polynomial(coeffs)

    def factor_out(self, n: int) -> Polynomial:
        p = Polynomial.zero()
        for power, coeff in self.coeffs.items():
            p[power - n] = coeff
        return p

    def __divmod__(self, other):
        if other.is_zero:
            raise ValueError("Can't divide by zero Polynomial")

        quotient = Polynomial.zero()
        remainder = deepcopy(self)

        while not remainder.is_zero and remainder.degree >= other.degree:
            power_r, coeff_r = remainder.leading_term
            power_d, coeff_d = other.leading_term
            # d for denominator
            power_tmp = power_r - power_d
            coeff_tmp = Fraction(coeff_r, coeff_d)
            tmp = Polynomial({power_tmp: coeff_tmp})

            quotient += tmp
            remainder -= tmp * other

        return (quotient, remainder)

    def d(self):
        coeffs = {(power - 1): power * coeff for power, coeff in self.coeffs.items()}
        return Polynomial(coeffs)
