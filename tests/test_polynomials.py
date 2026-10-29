from polynomials import Polynomial

from hypothesis import given, strategies as st
import pytest

# =====================
# Polynomial generators
# =====================


def polynomial(**kwargs):
    return st.builds(Polynomial.from_coeffs, st.lists(st.fractions(), **kwargs))


def nonzero_polynomial(**kwargs):
    return polynomial(**kwargs).filter(lambda p: p != Polynomial.zero())


def constant_polynomial():
    return st.builds(Polynomial.from_coeffs, st.fractions())


# ========
# Creation
# ========


def test_zero():
    lhs = Polynomial.zero()
    rhs = Polynomial.from_coeffs()
    assert lhs == rhs


# ============================
# Array Access on Coefficients
# ============================


@given(st.integers(min_value=0))
def test_get_any_coeff_of_zero_is_zero(power):
    coeff = Polynomial.zero()[power]
    assert coeff == 0


@given(st.integers(min_value=0), st.fractions())
def test_set_then_get_is_get(power, coeff):
    p = Polynomial.zero()
    p[power] = coeff
    assert p[power] == coeff


@given(polynomial(), st.integers(min_value=0))
def test_slice_decreases_degree(p, power):
    sliced = p.slice(0, power)
    assert sliced.degree <= p.degree
    assert sliced.degree <= power


# ========
# Addition
# ========


@given(polynomial())
def test_add_identity_element(a):
    add_zero_right = a + Polynomial.zero()
    add_zero_left = Polynomial.zero() + a
    assert a == add_zero_right
    assert a == add_zero_left


@given(polynomial(), polynomial())
def test_add_is_commutative(a, b):
    lhs = a + b
    rhs = b + a
    assert lhs == rhs


@given(polynomial(), polynomial(), polynomial())
def test_add_is_commutative(a, b, c):
    lhs = (a + b) + c
    rhs = a + (b + c)
    assert lhs == rhs


# ===========
# Subtraction
# ===========


@given(polynomial())
def test_sub_identity_element(a):
    rhs = a - Polynomial.zero()
    assert a == rhs


@given(polynomial())
def test_sub_of_self_is_zero(a):
    rhs = a - a
    assert Polynomial.zero() == rhs


@given(polynomial(), polynomial())
def test_sub_is_anticommutative(a, b):
    lhs = a - b
    rhs = -(b - a)
    assert lhs == rhs


# ==============
# Multiplication
# ==============


@given(polynomial())
def test_mult_identity_element(a):
    rhs = a * Polynomial.one()
    assert a == rhs


@given(polynomial())
def test_mult_absorbing_element(a):
    zero = Polynomial.zero()
    rhs = a * zero
    assert zero == rhs


@given(polynomial(), polynomial())
def test_mult_is_commutative(a, b):
    lhs = a * b
    rhs = b * a
    assert lhs == rhs


@given(polynomial(), polynomial(), polynomial())
def test_mult_is_associative(a, b, c):
    lhs = (a * b) * c
    rhs = a * (b * c)
    assert lhs == rhs


@given(polynomial(), polynomial(), polynomial())
def test_mult_distributes_over_add(a, b, c):
    lhs = a * (b + c)
    rhs = a * b + a * c
    assert lhs == rhs


@given(polynomial())
def test_mult_by_minus_one_is_add_inverse(a):
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
def test_divmod_identity_element(a):
    lhs_quotient, lhs_remainder = divmod(a, Polynomial.one())
    assert lhs_quotient == a
    assert lhs_remainder == Polynomial.zero()


@given(polynomial(), nonzero_polynomial())
def test_divmod_is_inverse_of_mult(a, b):
    quotient, remainder = divmod(a, b)
    inverse = quotient * b + remainder
    assert a == inverse


@given(nonzero_polynomial())
def test_divmod_by_one_is_mult_inverse(a):
    lhs_quotient, lhs_remainder = divmod(Polynomial.one(), a)
    assert lhs_quotient * a + lhs_remainder == Polynomial.one()


# ==============
# Exponentiation
# ==============


@given(nonzero_polynomial())
def test_exp_zero_rule(a):
    lhs = a**0
    assert lhs == Polynomial.one()


@given(
    nonzero_polynomial(max_size=5),
    st.integers(min_value=0, max_value=10),
    st.integers(min_value=0, max_value=10),
)
def test_exp_product_rule(a, m, n):
    lhs = a**m * a**n
    rhs = a ** (m + n)
    assert lhs == rhs


@given(
    nonzero_polynomial(max_size=4),
    st.integers(min_value=0, max_value=4),
    st.integers(min_value=0, max_value=4),
)
def test_exp_power_of_power_rule(a, m, n):
    lhs = (a**m) ** n
    rhs = a ** (m * n)
    assert lhs == rhs


@given(nonzero_polynomial(max_size=5), st.integers(min_value=0, max_value=10))
def test_fast_exp_equals_slow_exp(a, n):
    lhs = a**n
    rhs = a.slow_exp(n)
    assert lhs == rhs


# ===============
# Differentiation
# ===============


@given(nonzero_polynomial())
def test_diff_lowers_polynomial_degree(a):
    a_diff = a.d()
    assert a.degree > a_diff.degree


def test_derivative_of_zero_is_zero():
    lhs = Polynomial.zero()
    rhs = lhs.d()
    assert lhs == rhs


@given(constant_polynomial())
def test_diff_constant_term_rule(a):
    lhs = a.d()
    rhs = Polynomial.zero()
    assert lhs == rhs


@given(constant_polynomial(), polynomial())
def test_diff_constant_factor_rule(a, b):
    lhs = (a * b).d()
    rhs = a * b.d()
    assert lhs == rhs


@given(polynomial(), polynomial())
def test_diff_sum_rule(a, b):
    lhs = (a + b).d()
    rhs = a.d() + b.d()
    assert lhs == rhs


@given(polynomial(), polynomial())
def test_diff_difference_rule(a, b):
    lhs = (a - b).d()
    rhs = a.d() - b.d()
    assert lhs == rhs


@given(polynomial(), polynomial())
def test_diff_product_rule(a, b):
    lhs = (a * b).d()
    rhs = a.d() * b + a * b.d()
    assert lhs == rhs


# ==========
# Evaluation
# ==========


@given(nonzero_polynomial())
def test_eval_zero_is_constant(p):
    lhs = p(0)
    rhs = p[0]
    assert lhs == rhs


@given(nonzero_polynomial())
def test_eval_one_is_sum_of_coefficients(p):
    lhs = p(1)
    rhs = sum(p.coeffs.values())
    assert lhs == rhs


@given(
    polynomial(),
    # We have to set a limit on the maximum value we evaluate on
    # so we don't have numeric overflows in the test.
    st.one_of(
        st.integers(min_value=-1_000_000, max_value=1_000_000),
        st.fractions(min_value=-1_000_000, max_value=1_000_000),
        st.floats(min_value=-1_000_000, max_value=1_000_000),
    ),
)
def test_slow_eval_equals_fast_eval(p, x):
    lhs = p.fast_eval(x)
    rhs = p.slow_eval(x)
    assert lhs == rhs
