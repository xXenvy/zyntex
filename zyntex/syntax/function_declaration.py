from typing import Optional, List
from dataclasses import dataclass

from ..bindings import PyASTNode, NodeTag, PyString
from .node_element import INodeElement
from .type_node import TypeNode


class FunctionDeclaration(INodeElement):
    """Represents a Zig function declaration."""

    @dataclass
    class FunctionParam:
        name: str
        type: TypeNode

    __slots__ = ("_node",)

    def __init__(self, node: PyASTNode) -> None:
        self._node = node
        assert (self.is_node_valid(node)), "Provided node is not a function declaration."

    def __repr__(self) -> str:
        return f"FunctionDeclaration(name={self.name})"

    @staticmethod
    def is_node_valid(node: PyASTNode) -> bool:
        if node.tag == NodeTag.FN_DECL:
            return True
        return node.is_extern and node.tag in (
            NodeTag.FN_PROTO,
            NodeTag.FN_PROTO_ONE,
            NodeTag.FN_PROTO_SIMPLE,
            NodeTag.FN_PROTO_MULTI
        )

    @property
    def name(self) -> str:
        return self._node.spelling

    @property
    def body(self) -> Optional[str]:
        """Raw body of the function declaration. None if the function is declared with extern."""
        if self._node.tag == NodeTag.FN_DECL:
            return self._node.rhs_source

    @property
    def return_type(self) -> TypeNode:
        return_type: Optional[PyASTNode] = self._node.type
        assert return_type is not None, "The function doesn't have a return type."
        return TypeNode(return_type)

    @property
    def public(self) -> bool:
        """Whether the function is marked as pub."""
        return self._node.is_public()

    @property
    def extern(self) -> bool:
        """True, if the function is declared with extern."""
        return self._node.is_extern()

    @property
    def export(self) -> bool:
        """True, if the function is declared with export."""
        return self._node.is_export()

    @property
    def params(self) -> List[FunctionParam]:
        """List of function parameters."""
        result = []
        for param_data in self._node.params:
            result.append(
                FunctionDeclaration.FunctionParam(
                    name=param_data.name.to_list(PyString)[0],
                    type=TypeNode(PyASTNode(self._node.parent, param_data.type)),
                )
            )
        return result
