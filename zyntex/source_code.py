from __future__ import annotations
from typing import List, Type, Tuple

from .syntax import INodeElement, FunctionDeclaration, VariableDeclaration, TestDeclaration
from .bindings import PyTranslationUnit, ErrorReport, get_native_library


class SourceCode:
    """Represents a parsed source code.

    Parses the given source text into a translation unit and provides
    access to recognized top-level node elements."""

    __slots__ = ("_unit", "_source")

    def __init__(self, source: str) -> None:
        self._unit = PyTranslationUnit.from_source(lib=get_native_library(), source=source)
        self._source = source

    def __repr__(self) -> str:
        return f"SourceFile(size={len(self._source)})"

    @property
    def content(self) -> List[INodeElement]:
        """A list of top-level elements parsed from the source string."""
        result = []
        for node in self._unit.root_nodes():
            for node_type in self.types:
                if node_type.is_node_valid(node):
                    result.append(node_type(node))
        return result

    @property
    def types(self) -> Tuple[Type[INodeElement], ...]:
        """Supported top-level node element types."""
        return FunctionDeclaration, VariableDeclaration, TestDeclaration

    @property
    def errors(self) -> List[ErrorReport]:
        """A list of error reports that occurred during parsing this file."""
        return self._unit.errors()
