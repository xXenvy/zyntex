from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List

from .structures import ASTNode, NodeParam, PyString

if TYPE_CHECKING:
    from .translation_unit import PyTranslationUnit
    from .enums import NodeTag


class PyASTNode:
    """Represents a high-level Python wrapper for a single `ASTNode`.
    Provides convenient accessors for commonly used node information."""

    __slots__ = ("_parent", "_node", "_lib")

    def __init__(self, parent: PyTranslationUnit, node: ASTNode) -> None:
        self._parent = parent
        self._node = node
        self._lib = parent.lib

    def __repr__(self) -> str:
        return f"PyASTNode(tag={self.tag})"

    def is_public(self) -> bool:
        """True if the node is marked as pub."""
        return self._lib.isNodePublic(self._parent.ptr, self._node)

    def is_extern(self) -> bool:
        """True if the node is marked as extern."""
        return self._lib.isNodeExtern(self._parent.ptr, self._node)

    def is_export(self) -> bool:
        """True if the node is marked as export."""
        return self._lib.isNodeExport(self._parent.ptr, self._node)

    def is_container(self) -> bool:
        """True if the node is a container (Enum, Struct, Union, or Opaque)."""
        return self._lib.isNodeContainer(self._node)

    def is_const(self) -> bool:
        """Whether the node is marked as const."""
        return self._lib.isNodeConst(self._parent.ptr, self._node)

    def is_struct(self) -> bool:
        """Whether the node points to a struct."""
        return self._lib.isNodeStruct(self._parent.ptr, self._node)

    def is_union(self) -> bool:
        """Whether the node points to a union."""
        return self._lib.isNodeUnion(self._parent.ptr, self._node)

    def is_opaque(self) -> bool:
        """Whether the node points to an opaque."""
        return self._lib.isNodeOpaque(self._parent.ptr, self._node)

    def is_enum(self) -> bool:
        """Whether the node points to an enum."""
        return self._lib.isNodeEnum(self._parent.ptr, self._node)

    @property
    def tag(self) -> NodeTag:
        """The node's tag."""
        return self._node.tag

    @property
    def spelling(self) -> str:
        """The node's spelling as a decoded UTF-8 string."""
        return self._lib.getNodeSpelling(
            self._parent.ptr, self._node
        ).to_list(PyString)[0]

    @property
    def rhs_source(self) -> str:
        """The source text for the node's right-hand side (RHS)."""
        return self._lib.getNodeSource(
            self._parent.ptr, self.rhs
        ).to_list(PyString)[0]

    @property
    def rhs(self) -> int:
        """The index of the node right-hand side (RHS)."""
        return self._node.rhs

    @property
    def rhs_node(self) -> PyASTNode:
        """The node's right-hand side (RHS)."""
        ast_node = self._lib.getTranslationUnitNodeFromIndex(self._parent.ptr, self.rhs)
        return PyASTNode(parent=self.parent, node=ast_node)

    @property
    def lhs_source(self) -> str:
        """The source text for the node's left-hand side (LHS)."""
        return self._lib.getNodeSource(
            self._parent.ptr, self.lhs
        ).to_list(PyString)[0]

    @property
    def lhs(self) -> int:
        """The index of the node left-hand side (LHS)."""
        return self._node.lhs

    @property
    def lhs_node(self) -> PyASTNode:
        """The node's left-hand side (LHS)."""
        ast_node = self._lib.getTranslationUnitNodeFromIndex(self._parent.ptr, self.lhs)
        return PyASTNode(parent=self.parent, node=ast_node)

    @property
    def type(self) -> Optional[PyASTNode]:
        """The type node assigned to Node. For functions, it's the return type.
        For variable declarations, it specifies the type hint."""
        node_type = self._lib.getNodeType(self._parent.ptr, self._node)
        if node_type.index != self._node.index:
            return PyASTNode(self.parent, node_type)

    @property
    def body(self) -> Optional[str]:
        """Node's raw body."""
        body_slice = self._lib.getNodeBody(self._parent.ptr, self._node)
        if not body_slice.is_empty:
            return body_slice.to_list(PyString)[0]

    @property
    def params(self) -> List[NodeParam]:
        """A list of node's parameters. For functions, these are arguments"""
        result = []
        params_count = self._lib.getNodeParamsCount(self._parent.ptr, self._node)
        if params_count == 0:
            return result
        buffer = (NodeParam * params_count)()
        filled = self._lib.getNodeParams(self._parent.ptr, self._node, buffer, params_count)
        for i in range(filled):
            result.append(buffer[i])
        return result

    @property
    def align(self) -> Optional[str]:
        """The align value for the node."""
        align_slice = self._lib.getNodeAlign(self._parent.ptr, self._node)
        if not align_slice.is_empty:
            return align_slice.to_list(PyString)[0]

    @property
    def released(self) -> bool:
        """Indicates whether the ASTNode has been released."""
        return self._parent.released

    @property
    def parent(self) -> PyTranslationUnit:
        """The parent of this ASTNode."""
        return self._parent
