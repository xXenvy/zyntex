from typing import Optional, Union

from ..bindings import PyASTNode, NodeTag

from .lazy_init import LazyInit, lazy_invoke
from .node_element import INodeElement
from .type_node import TypeNode


class VariableDeclaration(INodeElement):
    """Represents a Zig variable declaration."""

    def __init__(
            self,
            name: Union[str, LazyInit],
            value: Union[str, None, LazyInit],
            type_hint: Union[TypeNode, None, LazyInit],
            alignment: Union[str, None, LazyInit] = None,
            is_public: Union[bool, LazyInit] = False,
            is_const: Union[bool, LazyInit] = False,
            is_extern: Union[bool, LazyInit] = False,
            is_export: Union[bool, LazyInit] = False,
    ) -> None:
        self._name = name
        self._value = value
        self._type_hint = type_hint
        self._alignment = alignment
        self._is_public = is_public
        self._is_const = is_const
        self._is_extern = is_extern
        self._is_export = is_export
        self._is_const = is_const

    @classmethod
    def from_node(cls, node: PyASTNode) -> "VariableDeclaration":
        assert cls.is_node_valid(node), "Provided node is not a variable declaration."
        lazy = LazyInit(node)
        return cls(
            name=lazy,
            value=lazy,
            type_hint=lazy,
            alignment=lazy,
            is_public=lazy,
            is_const=lazy,
            is_extern=lazy,
            is_export=lazy
        )

    @staticmethod
    def is_node_valid(node: PyASTNode) -> bool:
        return node.tag in (
            NodeTag.SIMPLE_VAR_DECL,
            NodeTag.LOCAL_VAR_DECL,
            NodeTag.GLOBAL_VAR_DECL,
            NodeTag.ALIGNED_VAR_DECL
        )

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
    def type_hint(self) -> Optional[TypeNode]:
        """The explicit Zig type annotation for the variable, if present."""
        assert isinstance(self._type_hint, LazyInit)
        node_type = self._type_hint.node.type
        if node_type:
            self._type_hint = TypeNode.from_node(node_type)
        else:
            self._type_hint = None
        return self._type_hint

    @type_hint.setter
    def type_hint(self, value: Optional[TypeNode]) -> None:
        self._type_hint = value

    @property
    @lazy_invoke
    def alignment(self) -> Optional[str]:
        """The explicit Zig alignment for the variable, if present."""
        assert isinstance(self._alignment, LazyInit)
        if self._alignment.node.tag in (
                NodeTag.LOCAL_VAR_DECL,
                NodeTag.GLOBAL_VAR_DECL,
                NodeTag.ALIGNED_VAR_DECL
        ):
            self._alignment = self._alignment.node.align
        else:
            self._alignment = None
        return self._alignment

    @alignment.setter
    def alignment(self, value: Optional[str]) -> None:
        self._alignment = value

    @property
    @lazy_invoke
    def value(self) -> Optional[str]:
        """The raw value of the variable. None if the variable is declared with extern."""
        assert isinstance(self._value, LazyInit)
        if not self.is_extern:
            self._value = self._value.node.body
        else:
            self._value = None
        return self._value

    @value.setter
    def value(self, value: Optional[str]) -> None:
        self._value = value

    @property
    @lazy_invoke
    def is_public(self) -> bool:
        """Whether the variable is marked as pub."""
        assert isinstance(self._is_public, LazyInit)
        self._is_public = self._is_public.node.is_public()
        return self._is_public

    @is_public.setter
    def is_public(self, value: bool) -> None:
        self._is_public = value

    @property
    @lazy_invoke
    def is_const(self) -> bool:
        """Whether the variable is declared with const."""
        assert isinstance(self._is_const, LazyInit)
        self._is_const = self._is_const.node.is_const()
        return self._is_const

    @is_const.setter
    def is_const(self, value: bool) -> None:
        self._is_const = value

    @property
    @lazy_invoke
    def is_extern(self) -> bool:
        """True, if the variable is declared with extern."""
        assert isinstance(self._is_extern, LazyInit)
        self._is_extern = self._is_extern.node.is_extern()
        return self._is_extern

    @is_extern.setter
    def is_extern(self, value: bool) -> None:
        self._is_extern = value

    @property
    @lazy_invoke
    def is_export(self) -> bool:
        """True, if the variable is declared with export."""
        assert isinstance(self._is_export, LazyInit)
        self._is_export = self._is_export.node.is_export()
        return self._is_export

    @is_export.setter
    def is_export(self, value: bool) -> None:
        self._is_export = value
