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
