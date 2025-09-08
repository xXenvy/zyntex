from typing import Union

from ..bindings import PyASTNode, NodeTag
from .lazy_init import LazyInit, lazy_invoke
from .node_element import INodeElement


class TestDeclaration(INodeElement):
    """Represents a Zig test declaration."""

    __slots__ = ("_name", "_body")

    def __init__(self, name: Union[str, LazyInit], body: Union[str, LazyInit]) -> None:
        self._name = name
        self._body = body

    @classmethod
    def from_node(cls, node: PyASTNode) -> "TestDeclaration":
        assert cls.is_node_valid(node), "Provided node is not a test declaration."
        lazy = LazyInit(node)
        return cls(name=lazy, body=lazy)

    @staticmethod
    def is_node_valid(node: PyASTNode) -> bool:
        return node.tag == NodeTag.TEST_DECL

    @property
    @lazy_invoke
    def name(self) -> str:
        assert isinstance(self._name, LazyInit)
        self._name = self._name.node.spelling
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    @lazy_invoke
    def body(self) -> str:
        """Raw body of the test."""
        assert isinstance(self._body, LazyInit)
        self._body = self._body.node.rhs_source
        return self._body

    @body.setter
    def body(self, value: str) -> None:
        self._body = value
