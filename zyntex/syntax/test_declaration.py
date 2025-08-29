from ..bindings import PyASTNode, NodeTag
from .node_element import INodeElement


class TestDeclaration(INodeElement):
    """Represents a Zig test declaration."""

    __slots__ = ("_node",)

    def __init__(self, node: PyASTNode) -> None:
        self._node = node
        assert (self.is_node_valid(node)), "Provided node is not a test declaration."

    def __repr__(self) -> str:
        return f"TestDeclaration(name={self.name})"

    @staticmethod
    def is_node_valid(node: PyASTNode) -> bool:
        return node.tag == NodeTag.TEST_DECL

    @property
    def name(self) -> str:
        return self._node.spelling

    @property
    def body(self) -> str:
        """Raw body of the test."""
        return self._node.rhs_source
