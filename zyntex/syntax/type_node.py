from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, cast, Union

from ..bindings import PyASTNode, NodeTag, PrimitiveType
from .node_element import INodeElement
from .lazy_init import LazyInit, lazy_invoke


class TypeNode(INodeElement):
    """A High-level wrapper for Zig Types.

    Provides methods to check if a type is an array, optional,
    pointer, or constant, and to access related subtypes.
    Distinguishes between primitive and custom (user-defined) types."""

    __slots__ = (
        "_array_type",
        "_array_length",
        "_optional_type",
        "_pointer_type",
        "_type",
        "_const"
    )

    @dataclass
    class CustomType:
        """Represents a non-primitive (user-defined) type name."""
        value: str

    def __init__(
            self,
            array_type: Union[TypeNode, None, LazyInit] = None,
            array_length: Union[str, None, LazyInit] = None,
            optional_type: Union[TypeNode, None, LazyInit] = None,
            pointer_type: Union[TypeNode, None, LazyInit] = None,
            type: Union[PrimitiveType, CustomType, None, LazyInit] = None,
            const: Union[bool, LazyInit] = False,
    ) -> None:
        self._array_type = array_type
        self._array_length = array_length
        self._optional_type = optional_type
        self._pointer_type = pointer_type
        self._type = type
        self._const = const

    @classmethod
    def from_node(cls, node: PyASTNode) -> "TypeNode":
        assert cls.is_node_valid(node), "Provided node is not a type."
        lazy = LazyInit(node)
        return cls(
            array_type=lazy,
            array_length=lazy,
            optional_type=lazy,
            pointer_type=lazy,
            type=lazy,
            const=lazy
        )

    @staticmethod
    def is_node_valid(node: PyASTNode) -> bool:
        return node.tag in (
            NodeTag.OPTIONAL_TYPE,
            NodeTag.ARRAY_TYPE,
            NodeTag.IDENTIFIER,
            NodeTag.PTR_TYPE_ALIGNED
        )

    def is_array(self) -> bool:
        return self.array_type is not None

    def is_optional(self) -> bool:
        return self.optional_type is not None

    def is_pointer(self) -> bool:
        return self.pointer_type is not None

    def is_type(self) -> bool:
        return self.type is not None

    @property
    @lazy_invoke
    def const(self) -> bool:
        assert isinstance(self._const, LazyInit)
        self._const = self._const.node.is_const()
        return self._const

    @const.setter
    def const(self, value: bool) -> None:
        self._const = value

    @property
    @lazy_invoke
    def array_length(self) -> Optional[str]:
        """Declared length of the array. None if the type node is not an array.

        The value is returned as a string because it may represent
        either a numeric literal or a symbolic name (variable/expression)."""
        assert isinstance(self._array_length, LazyInit)
        if self._array_length.node.tag == NodeTag.ARRAY_TYPE:
            self._array_length = self._array_length.node.lhs_source
        else:
            self._array_length = None
        return self._array_length

    @array_length.setter
    def array_length(self, value: Optional[str]) -> None:
        self._array_length = value

    @property
    @lazy_invoke
    def array_type(self) -> Optional[TypeNode]:
        """Type node of the array, or None if not an array."""
        assert isinstance(self._array_type, LazyInit)
        if self._array_type.node.tag == NodeTag.ARRAY_TYPE:
            self._array_type = TypeNode.from_node(self._array_type.node.rhs_node)
        else:
            self._array_type = None
        return self._array_type

    @array_type.setter
    def array_type(self, value: Optional[TypeNode]) -> None:
        self._array_type = value

    @property
    @lazy_invoke
    def optional_type(self) -> Optional[TypeNode]:
        """The inner type of optional, or None if not optional."""
        assert isinstance(self._optional_type, LazyInit)
        if self._optional_type.node.tag == NodeTag.OPTIONAL_TYPE:
            self._optional_type = TypeNode.from_node(self._optional_type.node.lhs_node)
        else:
            self._optional_type = None
        return self._optional_type

    @optional_type.setter
    def optional_type(self, value: Optional[TypeNode]) -> None:
        self._optional_type = value

    @property
    @lazy_invoke
    def pointer_type(self) -> Optional[TypeNode]:
        """The pointed-to type, or None if not a pointer."""
        assert isinstance(self._pointer_type, LazyInit)
        if self._pointer_type.node.tag == NodeTag.PTR_TYPE_ALIGNED:
            self._pointer_type = TypeNode.from_node(self._pointer_type.node.rhs_node)
        else:
            self._pointer_type = None
        return self._pointer_type

    @pointer_type.setter
    def pointer_type(self, value: Optional[TypeNode]) -> None:
        self._pointer_type = value

    @property
    @lazy_invoke
    def type(self) -> Optional[PrimitiveType | CustomType]:
        """Immediate type as PrimitiveType or CustomType, if identifier."""
        assert isinstance(self._type, LazyInit)
        if self._type.node.tag == NodeTag.IDENTIFIER:
            value = self._type.node.spelling
            try:
                self._type = PrimitiveType(value)
            except ValueError:
                self._type = self.CustomType(value)
        else:
            self._type = None
        return self._type

    @type.setter
    def type(self, value: Optional[PrimitiveType | CustomType]) -> None:
        self._type = value

    @property
    def absolute_type(self) -> Union[TypeNode.CustomType, PrimitiveType]:
        """Resolve the absolute base type.

        Walks through optional/array/pointer wrappers to locate the underlying
        identifier. Returns `PrimitiveType` for known primitives or `CustomType`
        for user-defined names. Raises `NotImplementedError` for unsupported type nodes."""
        current_node: TypeNode = self
        while True:
            if current_node.is_type():
                return cast(Union[TypeNode.CustomType, PrimitiveType], current_node.type)
            if current_node.is_optional():
                current_node = cast(TypeNode, current_node.optional_type)
            elif current_node.is_array():
                current_node = cast(TypeNode, current_node.array_type)
            elif current_node.is_pointer():
                current_node = cast(TypeNode, current_node.pointer_type)
            else:
                raise NotImplementedError(f"Type node ({current_node}) is not supported.")
