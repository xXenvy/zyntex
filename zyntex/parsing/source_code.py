from __future__ import annotations
from typing import Optional

from .syntax import (
    INodeElement,
    FunctionDeclaration,
    VariableDeclaration,
    TestDeclaration,
)
from .bindings import PyTranslationUnit, ErrorReport, get_native_library


class SourceCode:
    """Represents a parsed source code.

    Parses the given source text into a translation unit and provides
    access to recognized top-level node elements.

    Parameters
    ----------
    source:
        Source text to be parsed.
    lazy_parsing:
        If True, the underlying `PyTranslationUnit` will **not** be created
        during construction. Instead, parsing is deferred until the translation
        unit or other derived properties (like `.content`) are first accessed.

        .. versionadded:: 0.1.3
    """

    def __init__(self, source: str, lazy_parsing: bool = False) -> None:
        self._source = source

        self._unit: Optional[PyTranslationUnit] = None if lazy_parsing else (
            PyTranslationUnit.from_source(lib=get_native_library(), source=source)
        )
        self._content: Optional[list[INodeElement]] = None
        self._errors: Optional[list[ErrorReport]] = None

    def __repr__(self) -> str:
        return f"SourceFile(size={len(self._source)})"

    @property
    def content(self) -> list[INodeElement]:
        """A list of top-level elements parsed from the source string."""
        if self._content is None:
            self._content = []
            for node in self.unit.root_nodes():
                for node_type in self.types:
                    if node_type.is_node_valid(node):
                        self._content.append(node_type.from_node(node))
        return self._content

    @property
    def errors(self) -> list[ErrorReport]:
        """A list of error reports that occurred during parsing this file."""
        if self._errors is None:
            self._errors = self.unit.errors()
        return self._errors

    @property
    def unit(self) -> PyTranslationUnit:
        """
        The parsed translation unit for this source.

        .. versionadded:: 0.1.3
        """
        if self._unit is None:
            self._unit = PyTranslationUnit.from_source(
                lib=get_native_library(), source=self._source
            )
        return self._unit

    @property
    def types(self) -> tuple[type[INodeElement], ...]:
        """Supported top-level node element types."""
        return TestDeclaration, FunctionDeclaration, VariableDeclaration
