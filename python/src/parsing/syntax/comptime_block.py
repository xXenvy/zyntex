from typing import Union

from ..bindings import PyASTNode, NodeTag
from .lazy_init import LazyInit, lazy_invoke
from .node_element import INodeElement


class ComptimeBlock(INodeElement):
    """Represents a Zig comptime block with an unparsed string body.

    .. versionadded:: 0.3.3
    """

    def __init__(self, body: Union[str, LazyInit]) -> None:
        self._body = body

    @classmethod
    def from_node(cls, node: PyASTNode) -> "ComptimeBlock":
        assert cls.is_node_valid(node), "Provided node is not a comptime block."
        return cls(body=LazyInit(node))

    @staticmethod
    def is_node_valid(node: PyASTNode) -> bool:
        return node.tag == NodeTag.COMPTIME

    @property
    @lazy_invoke
    def body(self) -> str:
        """Raw block body, including braces and original formatting."""
        assert isinstance(self._body, LazyInit)
        body = self._body.node.body
        assert isinstance(body, str)
        self._body = body
        return self._body

    @body.setter
    def body(self, value: str) -> None:
        self._body = value
