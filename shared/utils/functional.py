"""
Either/Result monad implementation for functional error handling.

This module provides Either, Success, and Failure types for handling operations
that can succeed or fail without using exceptions. This is a thin wrapper around
the `returns` library's Result type with additional utility functions.
"""

from typing import Callable, TypeVar

from returns.result import Failure, Result, Success

__all__ = ['Either', 'Success', 'Failure', 'safe']

# Type alias for better readability
Either = Result

_T = TypeVar('_T')
_E = TypeVar('_E', bound=Exception)


def safe(
    function: Callable[..., _T],
) -> Callable[..., Either[_T, Exception]]:
    """
    Decorator to safely execute a function and return Either type.

    Wraps a function to catch exceptions and return them as Failure instead
    of propagating them. Successful execution returns Success.

    Args:
        function: The function to wrap

    Returns:
        A function that returns Either[T, Exception]

    Example:
        >>> @safe
        ... def divide(a: int, b: int) -> float:
        ...     return a / b
        >>> result = divide(10, 2)
        >>> isinstance(result, Success)
        True
        >>> result = divide(10, 0)
        >>> isinstance(result, Failure)
        True
    """
    from functools import wraps

    @wraps(function)
    def wrapper(*args, **kwargs) -> Either[_T, Exception]:
        try:
            return Success(function(*args, **kwargs))
        except Exception as e:
            return Failure(e)

    return wrapper
"""
Option/Maybe monad implementation for handling optional values.

This module provides Option, Some, and Nothing types for handling values that
may or may not exist without using None. This is a thin wrapper around the
`returns` library's Maybe type.
"""

from typing import TypeVar

from returns.maybe import Maybe, Nothing, Some

__all__ = ['Option', 'Some', 'Nothing']

# Type alias for better readability
Option = Maybe

_T = TypeVar('_T')
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
