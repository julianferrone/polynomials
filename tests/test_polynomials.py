from polynomials import Polynomial

from hypothesis import given, strategies as st
import pytest

# =====================
# Polynomial generators
# =====================


def polynomial():
    return st.builds(Polynomial.from_coeffs, st.lists(st.integers()))


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
