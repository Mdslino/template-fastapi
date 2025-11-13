"""
Functional programming utilities and composition helpers.

This module provides utilities for function composition and other functional
programming patterns.
"""

from typing import Callable, TypeVar

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_T3 = TypeVar('_T3')


def compose(
    f: Callable[[_T2], _T3], g: Callable[[_T1], _T2]
) -> Callable[[_T1], _T3]:
    """
    Compose two functions: compose(f, g)(x) = f(g(x)).

    Args:
        f: Function to apply second
        g: Function to apply first

    Returns:
        Composed function

    Example:
        >>> add_one = lambda x: x + 1
        >>> double = lambda x: x * 2
        >>> add_one_then_double = compose(double, add_one)
        >>> add_one_then_double(5)
        12
    """

    def composed(x: _T1) -> _T3:
        return f(g(x))

    return composed


def pipe(*functions: Callable) -> Callable:
    """
    Pipe functions left-to-right: pipe(f, g, h)(x) = h(g(f(x))).

    Args:
        *functions: Functions to pipe

    Returns:
        Piped function

    Example:
        >>> add_one = lambda x: x + 1
        >>> double = lambda x: x * 2
        >>> triple = lambda x: x * 3
        >>> pipeline = pipe(add_one, double, triple)
        >>> pipeline(5)
        36
    """
    from functools import reduce

    def piped(x):
        return reduce(lambda acc, f: f(acc), functions, x)

    return piped
