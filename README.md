# README

A Python library for performing arithmetic and algebraic operations on univariate polynomials.

## Features

- Represent univariate polynomials with integer or fractional coefficients
- Access polynomial coefficients, degree, and leading term
- Add, subtract, and negate polynomials
- Multiply polynomials
- Scale polynomials by a constant factor
- Divide polynomials (obtaining a quotient and a remainder)
- Exponentiate polynomials with an integer power
- Evaluate polynomials at a given (integer, fractional, or floating) point
- Differentiate polynomials
- Compose polynomials

## Install

I wrote this mostly as a bit of code kata, and to practice writing property
tests with Hypothesis. It's not intended to be installed.

## Usage

Create polynomials, specifying coefficients in standard form (descending order
of degree):

```python
from polynomials import Polynomial

p = Polynomial(3, 2, 1)
q = Polynomial(4, 5)

print(p)
print(q)

# Output:
```

```text
3x^2 + 2x + 1
4x + 5
```

```python
p[3] = 4 # p = 4x^3 + 3x^2 + 2x + 1
del p[3] # p = 3x^2 + 2x + 1

# Polynomial properties

p.degree         # 2
p.leading_term # 3x^2

# Arithmetic operations

print(-p)
print(p + q)
print(p - q)
print(p * q)

# Output:
```

```text
-3x^2 - 2x - 1
3x^2 + 6x + 6
3x^2 - 2x - 4
12x^3 + 23x^2 + 14x + 5
```

```python
# Division

quotient, remainder = divmod(p, q)

print(quotient)
print(remainder)

# Output:
```

```text
3x^2 + 2x + 1
4x + 5
```

```python
# Scaling and exponentiation

print(p.scale(2))
print(p**2)

# Output:
```

```text
6x^2 + 4x + 2
9x^4 + 12x^3 + 10x^2 + 4x + 1
```

```python
# Differentiation

print(p)
print(p.d())
print(p.d().d())

# Output:
```

```text
3x^2 + 2x + 1
6x + 2
6
```

```python
# Evaluate a polynomial

p(5) # 3*(5^2) + 2*5 + 1 = 86

# Compose polynomials

print(p << q)
print(q << p)

# Output:
```

```text
48x^2 + 128x + 86
12x^2 + 8x + 9
```
