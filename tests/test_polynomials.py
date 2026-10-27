from polynomials import Polynomial

from hypothesis import given, strategies as st
import pytest

# =====================
# Polynomial generators
# =====================


def polynomial():
    return st.builds(Polynomial.from_coeffs, st.lists(st.fractions()))


def nonzero_polynomial():
    return polynomial().filter(lambda p: p != Polynomial.zero())


# ========
# Creation
# ========


def test_zero():
    lhs = Polynomial.zero()
    rhs = Polynomial.from_coeffs()
    assert lhs == rhs


# ========
# Addition
# ========


@given(polynomial())
def test_additive_identity_element(a):
    add_zero_right = a + Polynomial.zero()
    add_zero_left = Polynomial.zero() + a
    assert a == add_zero_right
    assert a == add_zero_left


@given(polynomial(), polynomial())
def test_addition_is_commutative(a, b):
    lhs = a + b
    rhs = b + a
    assert lhs == rhs


@given(polynomial(), polynomial(), polynomial())
def test_addition_is_commutative(a, b, c):
    lhs = (a + b) + c
    rhs = a + (b + c)
    assert lhs == rhs


# ===========
# Subtraction
# ===========


@given(polynomial())
def test_subtraction_identity_element(a):
    rhs = a - Polynomial.zero()
    assert a == rhs


@given(polynomial())
def test_subtraction_of_self_is_zero(a):
    rhs = a - a
    assert Polynomial.zero() == rhs


@given(polynomial(), polynomial())
def test_subtraction_is_anticommutative(a, b):
    lhs = a - b
    rhs = -(b - a)
    assert lhs == rhs


# ==============
# Multiplication
# ==============


@given(polynomial())
def test_multiplication_identity_element(a):
    rhs = a * Polynomial.one()
    assert a == rhs


@given(polynomial())
def test_multiplication_absorbing_element(a):
    zero = Polynomial.zero()
    rhs = a * zero
    assert zero == rhs


@given(polynomial(), polynomial())
def test_multiplication_is_commutative(a, b):
    lhs = a * b
    rhs = b * a
    assert lhs == rhs


@given(polynomial(), polynomial(), polynomial())
def test_multiplication_is_associative(a, b, c):
    lhs = (a * b) * c
    rhs = a * (b * c)
    assert lhs == rhs


@given(polynomial(), polynomial(), polynomial())
def test_multiplication_distributes_over_addition(a, b, c):
    lhs = a * (b + c)
    rhs = a * b + a * c
    assert lhs == rhs


@given(polynomial())
def test_multiplication_by_minus_one_is_additive_inverse(a):
    lhs = -Polynomial.one() * a
    rhs = -a
    assert lhs == rhs
    sum_ = rhs + a
    assert sum_ == Polynomial.zero()


# =======
# Is Zero
# =======


def test_zero_polynomial_is_zero():
    assert Polynomial.zero().is_zero


@given(nonzero_polynomial())
def test_nonzero_polynomial_is_not_zero(a):
    assert not a.is_zero


# ========
# Division
# ========


@given(polynomial())
def test_division_identity_element(a):
    lhs_quotient, lhs_remainder = divmod(a, Polynomial.one())
    assert lhs_quotient == a
    assert lhs_remainder == Polynomial.zero()


@given(polynomial(), nonzero_polynomial())
def test_division_is_inverse_of_multiplication(a, b):
    quotient, remainder = divmod(a, b)
    inverse = quotient * b + remainder
    assert a == inverse


@given(nonzero_polynomial())
def test_division_by_one_is_multiplicative_inverse(a):
    lhs_quotient, lhs_remainder = divmod(Polynomial.one(), a)
    assert lhs_quotient * a + lhs_remainder == Polynomial.one()
