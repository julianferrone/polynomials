# README

A Python library for performing arithmetic and algebraic operations on univariate polynomials.

## Features

- Represent univariate polynomials with integer or fractional coefficients
- Addition, subtraction, negation, multiplication
- Division (obtaining a quotient and a remainder), floor division, and modulo
- Exponentiation with an integer power
- Shifting polynomials left, right, up, and down
- Scale polynomials by a constant factor
- Differentiation
- Indefinite and definite integration
- Access polynomial coefficients, degree, and leading term
- Compose polynomials
- Evaluate polynomials at a given (integer, fractional, or floating) value

## Install

I wrote this mostly as a bit of code kata, and to practice writing property
tests with Hypothesis. It's not intended to be installed.

## Usage Examples

### 1. Creating polynomials

```python
# 1.1. Using positional arguments (highest degree first)
p = Polynomial(1, 2, 3)
print(p)
# x^2 + 2x + 3

# 1.2. Using a list or tuple
p = Polynomial([2, -3, 5])
print(p)
# 2x^2 - 3x + 5

# 1.3. Using a dictionary (exponent: coefficient)
p = Polynomial({3: 4, 0: -1})
print(p)
# 4x^3 - 1
```

You can also use the built-in constructors:

```python
zero = Polynomial.zero()       # 0
one = Polynomial.one()         # 1
identity = Polynomial.identity()  # x

monomial = Polynomial.monomial(3, 2)
print(monomial)
# 2x^3
```

### 2. Arithmetic

Polynomials support the standard arithmetic operators.

```python
p = Polynomial(3, 2, 6)  # 3x^2 + 2x + 6
q = Polynomial(4, -1)    # 4x - 1

print(p + q)
# 3x^2 + 6x + 5

print(p - q)
# 3x^2 - 2x + 7

print(p * q)
# 12x^3 + 5x^2 + 22x - 6

print(-p)
# -3x^2 - 2x - 1

quotient, remainder = divmod(p, q)

print(quotient)
# (3/4)x + 11/16

print(remainder)
# 107/16

# Verify the division identity
print(quotient * q + remainder)
# 3x^2 + 2x + 6
```

You can also retrieve the quotient and remainder separately:

```python
quotient = p // q
remainder = p % q
```

Division by the zero polynomial raises a `ValueError`.

### 3. Exponentiation

Use the `**` operator to raise a polynomial to a non-negative integer power.

```python
p = Polynomial(1, 1)  # x + 1

print(p ** 2)
# x^2 + 2x + 1

print(p ** 3)
# x^3 + 3x^2 + 3x + 1
```

### 4. Transformations

Polynomials support vertical and horizontal shifts.

```python
p = Polynomial(1, 0, 0)  # x^2

# Shift vertically upwards by 3
print(p.shift_vertical(3))
# x^2 + 3

# Shift horizontally to the right by 2
print(p.shift_horizontal(2))
# x^2 - 4x + 4
```

You can also scale all coefficients:

```python
p = Polynomial(1, 2, 3)

print(p.scale(2))
# 2x^2 + 4x + 6
```

### 5. Differentiation

Use `diff` to calculate the derivative of a polynomial. Repeated
differentiation is supported through the `n` argument.

```python
p = Polynomial(4, 3, 2, 1)
# 4x^3 + 3x^2 + 2x + 1

print(p.diff())
# 12x^2 + 6x + 2

# Calculate the second derivative
print(p.diff(n=2))
# 24x + 6
```

### 6. Integration

Use `antidiff` to calculate an antiderivative / indefinite integral.

```python
p = Polynomial(1, 2, 3)
# x^2 + 2x + 3

print(p.antidiff())
# (1/3)x^3 + x^2 + 3x

# Specify the constant of integration
print(p.antidiff(4))
# (1/3)x^3 + x^2 + 3x + 4
```

You can also calculate definite integrals with `definite_integral`:

```python
p = Polynomial(1, 0, 0)  # x^2

print(p.definite_integral(0, 3))
# 9
```

### 7. Accessing and modifying coefficients

Coefficients can be accessed and modified using their corresponding exponents.

```python
p = Polynomial(1, 2, 3)
# x^2 + 2x + 3

# Retrieve the coefficient of x
print(p[1])
# 2

# Retrieve a missing coefficient
print(p[5])
# 0

# Change the coefficient of x
p[1] = 5

print(p)
# x^2 + 5x + 3

# Remove a term by setting its coefficient to zero
p[2] = 0

print(p)
# 5x + 3

# Or by deleting its coefficient
del p[0]

print(p)
# 5x
```

You can iterate over the individual terms:

```python
p = Polynomial({3: 4, 1: 2, 0: 5})

for power, coefficient in p:
    print(f"Power: {power}, Coefficient: {coefficient}")
```

Each iteration yields an `(exponent, coefficient)` pair.

### 8. Inspecting polynomial properties

The class exposes several useful properties.

```python
p = Polynomial(2, 0, 3)
# 2x^2 + 3

print(p.degree)
# 2

print(p.leading_term)
# (2, Fraction(2, 1))

print(p.is_zero)
# False

print(p.is_constant)
# False

print(p.is_monomial)
# False
```

You can also use a polynomial in a boolean context:

```python
if p:
    print("The polynomial is non-zero")
```

The zero polynomial has degree `-1` and evaluates to `False` when used as a
boolean.

### 9. Polynomial composition

The `compose` method substitutes one polynomial into another.

For example, given:

- \(p(x) = 2x + 1\)
- \(q(x) = 3x^2\)

Then \(p(q(x)) = 6x^2 + 1\).

```python
p = Polynomial(2, 1)
q = Polynomial(3, 0, 0)

print(p.compose(q))
# 6x^2 + 1
```

The `<<` operator is an alternative syntax for composition:

```python
print(p << q)
# 6x^2 + 1

print(q << p)
# 12x^2 + 12x + 3
```

Note that composition is not commutative: generally, `p << q` is not equal to
`q << p`.

### 10. Evaluating polynomials

Polynomials can be evaluated by calling them as functions.

```python
p = Polynomial(3, -2, 1)  # 3x^2 - 2x + 1

print(p(0))
# 1

print(p(1))
# 2

print(p(2))
# 9
```
