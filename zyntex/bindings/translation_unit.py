from __future__ import annotations

from ctypes import POINTER, CDLL, c_uint32
from typing import Optional, Any

from .structures import ErrorReport, TranslationUnit, ASTNode, ASTToken, PyString
from .ast_node import PyASTNode

TranslationUnitPtr = POINTER(TranslationUnit)


class PyTranslationUnit:
    """Represents a parsed translation unit for a single source file.

    Manages parsing, memory management, and provides convenient access
    to the underlying translation unit's resources at a higher level.
    """
    __slots__ = ("_tu_ptr", "_lib", "_path", "_released")

    def __init__(self, lib: CDLL, tu_ptr: Any, path: Optional[str] = None) -> None:
        self._tu_ptr = tu_ptr
        self._lib = lib
        self._path = path or "null"
        self._released = False

        if not self._tu_ptr:
            raise RuntimeError(
                f"Failed to parse translation unit from path: '{self._path}'. "
                f"The file may be missing, unreadable, or contain unrecoverable syntax errors."
            )

    @classmethod
    def from_path(cls, lib: CDLL, path: str) -> PyTranslationUnit:
        translation_unit_ptr = lib.createTranslationUnit(path.encode())
        return cls(lib=lib, tu_ptr=translation_unit_ptr, path=path)

    @classmethod
    def from_source(cls, lib: CDLL, source: str) -> PyTranslationUnit:
        translation_unit_ptr = lib.createTranslationUnitFromSource(source.encode())
        return cls(lib=lib, tu_ptr=translation_unit_ptr)

    def __del__(self) -> None:
        # Ensure resources are released when the instance is garbage collected.
        self.release()

    def __repr__(self) -> str:
        return f"PyTranslationUnit(path={self._path}, released={self._released})"

    def nodes_count(self) -> int:
        """Gets the total number of AST nodes within this translation unit."""
        return self._lib.getTranslationUnitNodesCount(self._tu_ptr)

    def tokens_count(self) -> int:
        """Retrieves the count of tokens parsed in the translation unit."""
        return self._lib.getTranslationUnitTokensCount(self._tu_ptr)

    def errors_count(self) -> int:
        """Retrieves the count of errors parsed in the translation unit."""
        return self._lib.getTranslationUnitErrorsCount(self._tu_ptr)

    def nodes(self) -> list[PyASTNode]:
        """A list of AST nodes parsed in the translation unit."""
        nodes = self._lib.getTranslationUnitNodes(self._tu_ptr).to_list(ASTNode)
        return list(map(lambda n: PyASTNode(self, n), nodes))

    def root_nodes(self) -> list[PyASTNode]:
        """The root AST nodes parsed in the translation unit."""
        root_nodes = []
        index_list = self._lib.getTranslationUnitRootNodes(self._tu_ptr).to_list(c_uint32)
        for index in index_list:
            node = self._lib.getTranslationUnitNodeFromIndex(self._tu_ptr, index)
            root_nodes.append(PyASTNode(self, node))
        return root_nodes

    def tokens(self) -> list[ASTToken]:
        """A list of AST tokens parsed in the translation unit."""
        return self._lib.getTranslationUnitTokens(self._tu_ptr).to_list(ASTToken)

    def errors(self) -> list[ErrorReport]:
        """A list of ErrorReport instances for all errors encountered during parsing.
        Parsing continues despite errors, so this list may contain multiple reports."""
        return self._lib.getTranslationUnitErrors(self._tu_ptr).to_list(ErrorReport)

    def release(self) -> None:
        """Manually release TranslationUnit memory.
        Once completed, unit resources will be no longer available."""
        if not self._released:
            self._released = True
            if self._tu_ptr:
                self._lib.freeTranslationUnit(self._tu_ptr)

    @property
    def source(self) -> str:
        """Fetches the full source code as a decoded UTF-8 string."""
        return self._lib.getTranslationUnitSource(self._tu_ptr).to_list(PyString)[0]

    @property
    def path(self) -> str:
        """The original file path used for parsing."""
        return self._path

    @property
    def released(self) -> bool:
        """Whether the translation unit has been released."""
        return self._released

    @property
    def ptr(self) -> Any:
        """Gets the low-level pointer to the translation unit."""
        return self._tu_ptr

    @property
    def lib(self) -> CDLL:
        """Gets the low-level ctypes.CDLL handle for the native parser library."""
        return self._lib
