from __future__ import annotations
from typing import List, Tuple, Type

from .syntax import INodeElement, FunctionDeclaration, VariableDeclaration, TestDeclaration
from .bindings import PyTranslationUnit, ErrorReport, get_native_library


class SourceFile:
    """Represents a parsed source file.

    Parses the given file into a translation unit and provides
    access to recognized top-level node elements."""

    __slots__ = ("_unit", "_types")

    def __init__(self, file_path: str) -> None:
        self._unit = PyTranslationUnit.from_path(lib=get_native_library(), path=file_path)

    def __repr__(self) -> str:
        return f"SourceFile(path={self.path})"

    @property
    def content(self) -> List[INodeElement]:
        """A list of top-level elements parsed from the file."""
        result = []
        for node in self._unit.root_nodes():
            for node_type in self.types:
                if node_type.is_node_valid(node):
                    result.append(node_type(node))
        return result

    @property
    def path(self) -> str:
        """The parsed file path."""
        return self._unit.path

    @property
    def types(self) -> Tuple[Type[INodeElement], ...]:
        """Supported top-level node element types."""
        return FunctionDeclaration, VariableDeclaration, TestDeclaration

    @property
    def errors(self) -> List[ErrorReport]:
        """A list of error reports that occurred during parsing this file."""
        return self._unit.errors()
