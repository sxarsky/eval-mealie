"""Formatting utilities for display of recipe ingredient quantities."""

from fractions import Fraction

INGREDIENT_QTY_PRECISION = 3

SUPERSCRIPT = dict(zip("1234567890", "¹²³⁴⁵⁶⁷⁸⁹⁰", strict=False))
SUBSCRIPT = dict(zip("1234567890", "₁₂₃₄₅₆₇₈₉₀", strict=False))


def display_fraction(fraction: Fraction):
    return (
        "".join([SUPERSCRIPT[c] for c in str(fraction.numerator)])
        + "/"
        + "".join([SUBSCRIPT[c] for c in str(fraction.denominator)])
    )
