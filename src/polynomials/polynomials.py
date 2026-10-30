from __future__ import annotations
from collections import defaultdict
from collections.abc import Iterable
from copy import deepcopy
from fractions import Fraction
from math import ceil


class Polynomial:
    coeffs: defaultdict[int, Fractional]

    # ------------
    # Constructors
    # ------------

    def __init__(self, *args):
        """Initialise a polynomial from a sequence of coefficients or a mapping
        of (integer) exponents to coefficients.

        Args:
            *args: Polynomial coefficients supplied as positional arguments, in
                standard form (ordered from highest degree to the constant term).
                Alternatively, coefficients may be supplied as a list or tuple
                in the same order, or as a mapping of exponents to coefficients.

        Examples:
            Initialise using positional arguments:
                >>> print(Polynomial(1, 2, 3))
                x^2 + 2x + 3

            Initialise using a tuple:
                >>> print(Polynomial((2, -3, 5)))
                2x^2 - 3x + 5

            Initialise using a list:
                >>> print(Polynomial([1, 2, 5, 14]))
                x^3 + 2x^2 + 5x + 14

            Initialise using a mapping:
                >>> print(Polynomial({3: 4, 0: -1}))
                4x^3 - 1
        """
        # Unpack if provided a single list/tuple/dictionary
        arg = args[0] if len(args) == 1 else args

        if isinstance(arg, dict):
            coeffs = arg
        elif isinstance(arg, (list, tuple)):
            # We need to iterate in reverse order so that users can
            # define the polynomials in standard form (i.e. highest
            # powers first:
            #
            # >>> print(Polynomial(1, -2, 3))
            # x^2 - 2x + 3
            coeffs = dict(enumerate(reversed(arg)))
        else:
            # Handle the constant term case
            coeffs = {0: arg}

        normalised_coeffs = {
            power: Fraction(coeff)
            for power, coeff in coeffs.items()
            if power >= 0 and coeff != 0
        }
        self.coeffs = defaultdict(Fraction, normalised_coeffs)

    @classmethod
    def zero(cls) -> Polynomial:
        """
        Creates the constant 0 polynomial.

        Returns:
            Polynomial: The polynomial with no non-zero coefficients.
        """
        return cls(0)

    @classmethod
    def one(cls) -> Polynomial:
        """
        Creates the constant 1 polynomial.

        Returns:
            Polynomial: The polynomial 1.
        """
        return cls(1)

    # ------------------
    # Coefficient Access
    # ------------------

    def __getitem__(self, power: int) -> Fraction:
        """
        Returns the coefficient at a given exponent.

        Arguments:
            power (int): The exponent.

        Returns:
            Fraction: The coefficient for the given exponent. Returns 0 if
                there is no coefficient.
        """
        return self.coeffs.get(power, Fraction(0))

    def __setitem__(self, power: int, coeff: Fraction):
        """
        Sets the coefficient for a given exponent.

        Arguments:
            power (int): The exponent.
            coeff (Fraction): The coefficient to set.
        """
        if 0 > power:
            pass
        elif coeff == 0:
            del self[power]
        else:
            self.coeffs[power] = coeff

    def __delitem__(self, power: int):
        """
        Deletes the coefficient for a given exponent.

        Arguments:
            power (int): The exponent.
        """
        # `del self.coeffs[power]` would fail with a KeyError if the power isn't
        # found. We want deletion to be an idempotent operation, so we `pop` and
        # don't return the coefficient.
        self.coeffs.pop(power, None)

    def __iter__(self) -> Iterator[tuple[int, Fraction]]:
        """
        Returns an iterator of the individual terms in the polynomial.

        Returns:
            Iterator[tuple[int, Fraction]]: An iterator of the terms in the
            polynomial. Each term is a tuple of an exponent (int) and its
            associated coefficient (Fraction).
        """
        yield from self.coeffs.items()

    def split(self, split_at: int) -> tuple[Polynomial, Polynomial]:
        """Splits a polynomial into lower and higher-degree parts.

        Partition the terms at the given exponent, returning two polynomials
        such that `self == lower + upper * x**split_at`. The lower polynomial
        contains terms with exponents less than `split_at`. The upper
        polynomial contains terms with exponents greater than or equal to
        `split_at`, with their exponents shifted down by `split_at`.

        Arguments:
            split_at (int): The exponent at which to split the polynomial.

        Returns:
            tuple[Polynomial, Polynomial]: The lower- and upper-degree parts
            of the polynomial.
        """
        lower = Polynomial.zero()
        upper = Polynomial.zero()
        for power, coeff in self:
            if power < split_at:
                lower[power] = coeff
            else:
                upper[power - split_at] = coeff
        return (lower, upper)

    def slice(self, start: int, end: int) -> Polynomial:
        """
        Returns a polynomial containing terms with exponents in the range
        [start, end).

        Arguments:
            start (int): The lower bound on exponents (inclusive).
            end (int): The upper bound on exponents (exclusive).

        Returns:
            Polynomial: A new polynomial containing only terms whose exponents
            satisfy *start <= power < end*.
        """
        coeffs = {
            power: coeff for power, coeff in self if start <= power and power < end
        }
        return Polynomial(coeffs)

    # ------------------
    # Printing to String
    # ------------------

    def __str__(self) -> str:
        """Human-readable string representation of a Polynomial."""

        def term(power, coeff):
            if power == 0:
                return str(coeff)
            else:
                coeff = "" if coeff == 1 else str(coeff)
                power = "" if power == 1 else f"^{power}"
                return f"{coeff}x{power}"

        parts = iter(sorted(self, reverse=True))

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
        """Whether the polynomial is the zero polynomial."""
        return False if self.coeffs else True

    @property
    def degree(self) -> int:
        """Returns the degree of the polynomial. As Polynomials are univariate,
        this is the highest exponent occurring in the polynomial.

        Returns:
            int: The degree of the polynomial. *-1* if the polynomial is the
            zero polynomial.
        """
        # Convention for empty polynomials is that they have a degree of
        # negative infinity, but this would require returning a float.
        if self.is_zero:
            return -1
        return max(self.coeffs.keys())

    @property
    def leading_term(self) -> tuple[int, Fraction]:
        """Returns the term with the highest exponent in the polynomial.

        Returns:
            tuple[int, Fraction]: The term with the highest exponent in the
            polynomial. The term consists of the expoonent (int) and its
            associated coefficient (Fraction).
        """
        return max(self, default=(0, Fraction(0)), key=lambda pair: pair[0])

    # --------------------
    # Algebraic Operations
    # --------------------

    # .....................
    # Arithmetic Operations
    # .....................

    def __eq__(self, other: Polynomial) -> bool:
        """Compares two polynomials by their coefficients."""
        return self.coeffs == other.coeffs

    def __add__(self, other: Polynomial) -> Polynomial:
        """Add two polynomials together.

        Args:
            other (Polynomial): the second summand polynomial.

        Returns:
            Polynomial: the sum of the two polynomials.
        """
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
        p = deepcopy(self)
        for power, coeff in other:
            p[power] += coeff
        return p

    def __neg__(self):
        """Return a new polynomial with every coefficient negated."""
        return Polynomial({power: -coeff for power, coeff in self})

    def __sub__(self, other):
        """Subtract one polynomial from another.

        Args:
            other (Polynomial): the term to subtract.

        Returns:
            Polynomial: the difference of the two polynomials.
        """
        return self + -other

    def __mul__(self, other):
        """Multiply two polynomials together.

        Args:
            other (Polynomial): the second factor.

        Returns:
            Polynomial: the product of the two polynomials.
        """
        return self.fast_mul(other)

    def fast_mul(self, other):
        """Multiply two polynomials together. Implements Karatsuba's
        multiplication algorithm on polynomials.

        Args:
            other (Polynomial): the second factor.

        Returns:
            Polynomial: the product of the two polynomials.
        """
        tasks = []
        values = []
        tasks.append(("mul", self, other))
        # Morally, I'd like to implement Karatsuba with a recursive solution,
        # but Python will fail with a stack overflow exception on
        # decently-sized polynomials. So I need to manually track tasks (which
        # stores information about divide-and-conquer multiplications that need
        # to be recursed into, as well as when to combine these) and values
        # (executed multiplications).
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

                p_lower, p_upper = p.split(m)
                q_lower, q_upper = q.split(m)

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
        """Multiply two polynomials together. Implements naive multiplication
        on polynomials.

        Args:
            other (Polynomial): the second factor.

        Returns:
            Polynomial: the product of the two polynomials.
        """
        # n^2 multiplication
        p = Polynomial.zero()
        for power_a, coeff_a in self:
            for power_b, coeff_b in other:
                p[power_a + power_b] += coeff_a * coeff_b
        return p

    def scale(self, factor: int | Fraction) -> Polynomial:
        """Returns a new polynomial with all coefficients scaled by the given
        factor.

        Args:
            factor (int | Fraction): The scaling factor.

        Returns:
            Polynomial: the scaled polynomial.
        """
        return Polynomial({power: coeff * factor for power, coeff in self})

    def factor_out(self, n: int) -> Polynomial:
        """Returns a new polynomial with all exponents shifted downwards by `n`.

        Args:
            n (int): The degree to shift down by.

        Returns:
            Polynomial: the shifted polynomial.
        """
        return Polynomial({(power - n): coeff for power, coeff in self})

    def __divmod__(self, other: Polynomial) -> tuple[Polynomial, Polynomial]:
        """Returns the quotient and remainder of polynomial division.

        Args:
            other(Polynomial): The divisor polynomial. Must be non-zero.

        Returns:
            tuple[Polynomial, Polynomial]: A tuple containing the quotient and
            remainder of division, such that *self == quotient * other +
            remainder*.

        Raises:
            ValueError: if `other` is the zero polynomial.

        Examples:

        >>> p = Polynomial(3, 2, 6)
        >>> str(p)
        '3x^2 + 2x + 6'
        >>> q = Polynomial(4, 1)
        >>> str(q)
        '4x + 1'
        >>> (quotient, remainder) = divmod(p, q)
        >>> str(quotient)
        '3/4x + 5/16'
        >>> str(remainder)
        '91/16'
        >>> str(quotient * q + remainder)
        '3x^2 + 2x + 6'
        """
        if other.is_zero:
            raise ValueError("Can't divide by zero Polynomial")

        quotient = Polynomial.zero()
        remainder = deepcopy(self)

        # Implements long division
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

    def __pow__(self, n: int) -> Polynomial:
        """Raise the polynomial to a non-negative integer power.

        Args:
            n (int): The exponent. Must be a non-negative integer.

        Returns:
            Polynomial: The polynomial raised to the power n.

        Raises:
            ValueError: if n is not an integer, a negative integer, or if both
            the polynomial and n are zero.

        Examples:

        >>> p = Polynomial(1, 1)
        >>> str(p)
        'x + 1'
        >>> str(p**2)
        'x^2 + 2x + 1'
        >>> str(p**3)
        'x^3 + 3x^2 + 3x + 1'
        """
        return self.fast_exp(n)

    def fast_exp(self, n: int) -> Polynomial:
        """Raise the polynomial to a non-negative integer power using
        exponentiation by squaring.

        Args:
            n (int): The exponent. Must be a non-negative integer.

        Returns:
            Polynomial: The polynomial raised to the power n.

        Raises:
            ValueError: if n is not an integer, a negative integer, or if both
            the polynomial and n are zero.
        """
        if not isinstance(n, int):
            raise ValueError("Can't exponentiate by non-integer")
        if n < 0:
            raise ValueError("Can't exponentiate by negative integer")
        if self.is_zero and n == 0:
            raise ValueError("Can't exponentiate zero Polynomial by zero")
        if self.is_zero:
            return Polynomial.zero()
        if n == 0:
            return Polynomial.one()
        x = deepcopy(self)
        y = Polynomial.one()
        while n > 1:
            if n % 2 == 1:
                y = x * y
                n = n - 1
            x = x * x
            n = n // 2
        p = x * y
        assert isinstance(p, Polynomial)
        return p

    def slow_exp(self, n: int) -> Polynomial:
        """Raise the polynomial to a non-negative integer power using
        naive exponentiation.

        Args:
            n (int): The exponent. Must be a non-negative integer.

        Returns:
            Polynomial: The polynomial raised to the power n.

        Raises:
            ValueError: if n is not an integer, a negative integer, or if both
            the polynomial and n are zero.
        """
        if not isinstance(n, int):
            raise ValueError("Can't exponentiate by non-integer")
        if n < 0:
            raise ValueError("Can't exponentiate by negative integer")
        if self.is_zero and n == 0:
            raise ValueError("Can't exponentiate zero Polynomial by zero")
        if self.is_zero:
            return Polynomial.zero()
        if n == 0:
            return Polynomial.one()
        p = Polynomial.one()
        for _ in range(n):
            p *= self
        return p

    # ...................
    # Function Operations
    # ...................

    def diff(self, n: int = 1) -> Polynomial:
        """Return the nth derivative of the polynomial.

        Args:
            n: Which derivative to take.

        Returns:
            Polynomial: the derivative polynomial.

        Examples:

        >>> p = Polynomial(4, 3, 2, 1)
        >>> str(p)
        '4x^3 + 3x^2 + 2x + 1'
        >>> str(p.diff())
        '12x^2 + 6x + 2'
        >>> str(p.diff(n=2))
        '24x + 6'
        """
        # For any polynomial with degree d, d + 1 differentiations will take
        # that polynomial to the zero polynomial. This early check ensures that
        # the max running time of `diff` is linearly proportional to the degree
        # of the polynomial.
        #
        # e.g. d(x^3, 4) = d(3x^2, 3) = d(6x, 2) = d(6, 1) = d(0, 0)
        if self.degree < n:
            return Polynomial.zero()

        p = deepcopy(self)
        # This is something of a naive implementation considering we have to
        # perform n operations for n derivatives, but the earlier check ensures
        # that we're only ever performing at most d differentiations for a
        # d-degree polynomial. So it should be plenty fast enough.
        for _ in range(n):
            p = Polynomial({(power - 1): power * coeff for power, coeff in p})
        return p

    def __call__(self, x: int | float | Fraction) -> int | float | Fraction:
        """Evaluate a polynomial at a given value.

        Args:
            x (int | float | Fraction): the value to evaluate the polynomial
            at.

        Returns:
            int | float | Fraction: the computed value.

        Examples:

        >>> p = Polynomial(3, -2, 1)
        >>> str(p)
        '3x^2 - 2x + 1'
        >>> p(0)
        1
        >>> p(1)
        2
        >>> p(2)
        9
        """
        return self.fast_eval(x)

    def fast_eval(self, x):
        """Evaluate a polynomial at a given value using Horner's rule for
        performance.

        Args:
            x (int | float | Fraction): the value to evaluate the polynomial
            at.

        Returns:
            int | float | Fraction: the computed value.
        """
        # Implements Horner's rule for evaluating a polynomial
        result = self[self.degree]
        for power in range(self.degree - 1, -1, -1):
            result *= x
            result += self[power]
        if isinstance(x, float):
            return float(x)
        if result.is_integer():
            return int(result)
        return result

    def slow_eval(self, x):
        """Evaluate a polynomial at a given value using naive evaluation.

        Args:
            x (int | float | Fraction): the value to evaluate the polynomial
            at.

        Returns:
            int | float | Fraction: the computed value.
        """
        result = sum((coeff * x**power for power, coeff in self))
        if isinstance(x, float):
            return float(x)
        if result.is_integer():
            return int(result)
        return result

    def __lshift__(self, other):
        """Return the composition of this polynomial with another polynomial.

        Args:
            other (Polynomial): The polynomial to substitue for the variable in
            this polynomial.

        Returns:
            Polynomial: The composed polynomial which evaluates x as
            self(other(x)).

        Examples:

        >>> p = Polynomial(2, 1)
        >>> q = Polynomial(3, 0, 0)
        >>> str(p)
        '2x + 1'
        >>> str(q)
        '3x^2'
        >>> str(p << q)
        '6x^2 + 1'
        >>> str(q << p)
        '12x^2 + 12x + 3'
        """
        return self.compose(other)

    def compose(self, other: Polynomial) -> Polynomial:
        """Return the composition of this polynomial with another polynomial.

        Args:
            other (Polynomial): The polynomial to substitue for the variable in
            this polynomial.

        Returns:
            Polynomial: The composed polynomial which evaluates x as
            self(other(x)).
        """
        # Implements Horner's rule for evaluating a polynomial, but does
        # multiplication and addition on polynomials instead of fractional
        # coefficients. This lets us efficiently substitute the `other`
        # polynomial in for the variables in `self`.
        result = Polynomial(self[self.degree])
        for power in range(self.degree - 1, -1, -1):
            result *= other
            result += Polynomial(self[power])
        return result
