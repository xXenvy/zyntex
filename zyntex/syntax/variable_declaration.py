from typing import Optional

from ..bindings import PyASTNode, NodeTag
from .node_element import INodeElement
from .type_node import TypeNode


class VariableDeclaration(INodeElement):
    """Represents a Zig variable declaration."""

    __slots__ = ("_node",)

    def __init__(self, node: PyASTNode) -> None:
        self._node = node
        assert (self.is_node_valid(node)), "Provided node is not a variable declaration."

    def __repr__(self) -> str:
        return f"VariableDeclaration(name={self.name})"

    @staticmethod
    def is_node_valid(node: PyASTNode) -> bool:
        return node.tag in (
            NodeTag.SIMPLE_VAR_DECL,
            NodeTag.LOCAL_VAR_DECL,
            NodeTag.GLOBAL_VAR_DECL,
            NodeTag.ALIGNED_VAR_DECL
        )

    @property
    def name(self) -> str:
        return self._node.spelling

    @property
    def type_hint(self) -> Optional[TypeNode]:
        """The explicit Zig type annotation for the variable, if present."""
        node_type = self._node.type
        if node_type:
            return TypeNode(node_type)

    @property
    def alignment(self) -> Optional[str]:
        """The explicit Zig alignment for the variable, if present."""
        if self._node.tag == NodeTag.ALIGNED_VAR_DECL:
            return self._node.lhs_source
        if self._node.tag in (NodeTag.LOCAL_VAR_DECL, NodeTag.GLOBAL_VAR_DECL):
            return self._node.align

    @property
    def value(self) -> Optional[str]:
        """The raw value of the variable. None if the variable is declared with extern."""
        if not self.extern:
            return self._node.rhs_source

    @property
    def public(self) -> bool:
        """Whether the variable is marked as pub."""
        return self._node.is_public()

    @property
    def const(self) -> bool:
        """Whether the variable is declared with const."""
        return self._node.is_const()

    @property
    def extern(self) -> bool:
        """True, if the variable is declared with extern."""
        return self._node.is_extern()

    @property
    def export(self) -> bool:
        """True, if the variable is declared with export."""
        return self._node.is_export()
