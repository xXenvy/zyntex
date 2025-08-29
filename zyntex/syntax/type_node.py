from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, cast, Union

from ..bindings import PyASTNode, NodeTag, PrimitiveType
from .node_element import INodeElement


class TypeNode(INodeElement):
    """A High-level wrapper for Zig Types.

    Provides methods to check if a type is an array, optional,
    pointer, or constant, and to access related subtypes.
    Distinguishes between primitive and custom (user-defined) types."""

    @dataclass
    class CustomType:
        """Represents a non-primitive (user-defined) type name."""
        value: str

    __slots__ = ("_node",)

    def __init__(self, node: PyASTNode) -> None:
        self._node = node
        assert self.is_node_valid(node), "Provided node is not a type."

    def __repr__(self) -> str:
        return (f"NodeType("
                f"spelling={self._node.spelling}, "
                f"is_array={self.is_array()}, "
                f"is_optional={self.is_optional()}, "
                f"is_ptr={self.is_ptr()}, "
                f"is_type={self.is_type()})")

    @staticmethod
    def is_node_valid(node: PyASTNode) -> bool:
        return node.tag in (
            NodeTag.OPTIONAL_TYPE,
            NodeTag.ARRAY_TYPE,
            NodeTag.IDENTIFIER,
            NodeTag.PTR_TYPE_ALIGNED
        )

    def is_array(self) -> bool:
        return self._node.tag == NodeTag.ARRAY_TYPE

    def is_optional(self) -> bool:
        return self._node.tag == NodeTag.OPTIONAL_TYPE

    def is_ptr(self) -> bool:
        return self._node.tag == NodeTag.PTR_TYPE_ALIGNED

    def is_type(self) -> bool:
        return self._node.tag == NodeTag.IDENTIFIER

    def is_const(self) -> bool:
        return self._node.is_const()

    @property
    def spelling(self) -> str:
        """The spelling of the current node."""
        return self._node.spelling

    @property
    def array_length(self) -> Optional[str]:
        """Declared length of the array.

        The value is returned as a string because it may represent
        either a numeric literal or a symbolic name (variable/expression)."""
        if self.is_array():
            return self._node.lhs_source

    @property
    def array_type(self) -> Optional[TypeNode]:
        """Type node of the array, or None if not an array."""
        if self.is_array():
            return TypeNode(self._node.rhs_node)

    @property
    def optional_type(self) -> Optional[TypeNode]:
        """The inner type of optional, or None if not optional."""
        if self.is_optional():
            return TypeNode(self._node.lhs_node)

    @property
    def ptr_type(self) -> Optional[TypeNode]:
        """The pointed-to type, or None if not a pointer."""
        if self.is_ptr():
            return TypeNode(self._node.rhs_node)

    @property
    def type(self) -> Optional[PrimitiveType | CustomType]:
        """Immediate type as PrimitiveType or CustomType, if identifier."""
        if self.is_type():
            value = self._node.spelling
            try:
                return PrimitiveType(value)
            except ValueError:
                return self.CustomType(value)

    @property
    def absolute_type(self) -> Union[TypeNode.CustomType, PrimitiveType]:
        """Resolve the absolute base type.

        Walks through optional/array/pointer wrappers to locate the underlying
        identifier. Returns `PrimitiveType` for known primitives or `CustomType`
        for user-defined names. Raises `NotImplementedError` for unsupported nodes."""
        current_node: TypeNode = self
        while True:
            if current_node.is_type():
                return cast(Union[TypeNode.CustomType, PrimitiveType], current_node.type)
            if current_node.is_optional():
                current_node = cast(TypeNode, current_node.optional_type)
            elif current_node.is_array():
                current_node = cast(TypeNode, current_node.array_type)
            elif current_node.is_ptr():
                current_node = cast(TypeNode, current_node.ptr_type)
            else:
                raise NotImplementedError(f"Type node ({current_node}) is not supported.")
