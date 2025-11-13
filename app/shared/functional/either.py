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
