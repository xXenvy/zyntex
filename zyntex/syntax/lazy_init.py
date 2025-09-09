from __future__ import annotations

from functools import wraps
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..bindings import PyASTNode


class LazyInit:
    """Marker object that carries a PyASTNode to support lazy attribute init.

    Instances of this class are stored on objects to indicate that the real
    attribute value should be computed later from the provided AST node."""

    def __init__(self, node: PyASTNode) -> None:
        self.node = node


def lazy_invoke(func: Callable):
    """A decorator for lazy properties.

    Apply this to a @property method so its value is computed only on first
    access and then reused. The computed value is stored on a private
    attribute named `_<property_name>`. If that attribute is a `LazyInit` marker,
    the wrapped function will run to produce the value."""
    attr_name = f"_{func.__name__}"

    @wraps(func)
    def wrapper(self):
        try:
            value = getattr(self, attr_name)
        except AttributeError:
            return func(self)
        if isinstance(value, LazyInit):
            return func(self)
        return value

    return wrapper
