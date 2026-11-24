from dataclasses import dataclass
from typing import Optional, Union

from ..bindings import PyASTNode, NodeTag, PyString
from .lazy_init import LazyInit, lazy_invoke
from .node_element import INodeElement


class FunctionDeclaration(INodeElement):
    """Represents a Zig function declaration."""

    @dataclass
    class FunctionParam:
        """A parameter in a Zig function declaration.

        ``name`` is the parameter's identifier, and ``type`` is its type as
        written in Zig source. For ``count: u32``, ``name`` is ``"count"`` and
        ``type`` is ``"u32"``. An unnamed parameter such as ``u32`` in an
        ``extern`` declaration has ``name=None`` and ``type="u32"``.

        Generic parameters can use ``type="anytype"``. A variadic marker is
        stored as an entry with ``name=None`` and ``type="..."`` so the printer
        can reproduce it in the parameter list.
        """

        type: str
        name: Optional[str] = None
        is_comptime: bool = False
        is_noalias: bool = False

    def __init__(
            self,
            name: Union[str, LazyInit],
            body: Union[str, None, LazyInit],
            return_type: Union[str, LazyInit],
            params: Union[list[FunctionParam], None, LazyInit] = None,
            is_public: Union[bool, LazyInit] = False,
            is_extern: Union[bool, LazyInit] = False,
            is_export: Union[bool, LazyInit] = False,
    ) -> None:
        self._name = name
        self._body = body
        self._return_type = return_type
        self._params = [] if params is None else params
        self._is_public = is_public
        self._is_extern = is_extern
        self._is_export = is_export

    @classmethod
    def from_node(cls, node: PyASTNode) -> "FunctionDeclaration":
        assert cls.is_node_valid(node), "Provided node is not a function declaration."
        lazy = LazyInit(node)
        return cls(
            name=lazy,
            body=lazy,
            return_type=lazy,
            is_public=lazy,
            is_extern=lazy,
            is_export=lazy,
            params=lazy
        )

    @staticmethod
    def is_node_valid(node: PyASTNode) -> bool:
        if node.tag == NodeTag.FN_DECL:
            return True
        return node.is_extern() and node.tag in (
            NodeTag.FN_PROTO,
            NodeTag.FN_PROTO_ONE,
            NodeTag.FN_PROTO_SIMPLE,
            NodeTag.FN_PROTO_MULTI
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
    def body(self) -> Optional[str]:
        """Raw body of the function declaration. None if the function is declared with extern."""
        assert isinstance(self._body, LazyInit)
        if self._body.node.tag == NodeTag.FN_DECL:
            self._body = self._body.node.body
        else:
            self._body = None
        return self._body

    @body.setter
    def body(self, value: Optional[str]) -> None:
        self._body = value

    @property
    @lazy_invoke
    def return_type(self) -> str:
        """The return type as Zig source, including any inferred error marker."""
        assert isinstance(self._return_type, LazyInit)
        return_type = self._return_type.node.type
        if return_type is None:
            raise ValueError("The function doesn't have a return type.")
        self._return_type = return_type
        return self._return_type

    @return_type.setter
    def return_type(self, value: str) -> None:
        self._return_type = value

    @property
    @lazy_invoke
    def params(self) -> list[FunctionParam]:
        """List of function parameters."""
        assert isinstance(self._params, LazyInit)
        node = self._params.node
        params = []
        for param in node.params:
            params.append(self.FunctionParam(
                type=param.type.to_list(PyString)[0],
                name=param.name.to_list(PyString)[0] or None,
                is_comptime=param.is_comptime,
                is_noalias=param.is_noalias,
            ))
        self._params = params
        return self._params

    @params.setter
    def params(self, value: list[FunctionParam]) -> None:
        self._params = value

    @property
    @lazy_invoke
    def is_public(self) -> bool:
        """Whether the function is marked as pub."""
        assert isinstance(self._is_public, LazyInit)
        self._is_public = self._is_public.node.is_public()
        return self._is_public

    @is_public.setter
    def is_public(self, value: bool) -> None:
        self._is_public = value

    @property
    @lazy_invoke
    def is_extern(self) -> bool:
        """True, if the function is declared with extern."""
        assert isinstance(self._is_extern, LazyInit)
        self._is_extern = self._is_extern.node.is_extern()
        return self._is_extern

    @is_extern.setter
    def is_extern(self, value: bool) -> None:
        self._is_extern = value

    @property
    @lazy_invoke
    def is_export(self) -> bool:
        """True, if the function is declared with export."""
        assert isinstance(self._is_export, LazyInit)
        self._is_export = self._is_export.node.is_export()
        return self._is_export

    @is_export.setter
    def is_export(self, value: bool) -> None:
        self._is_export = value
