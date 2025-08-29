import ctypes
from typing import List

from .enums import ErrorTag, NodeTag, TokenTag


class PyString:
    """A special type for GenericSlice to treat an entire array of bytes as a single py string."""


class TranslationUnit(ctypes.Structure):
    """Represents a parsed translation unit from the Zig AST."""


class GenericSlice(ctypes.Structure):
    """A generic container for FFI slices, representing a pointer and it's length."""

    _fields_ = [
        ("ptr", ctypes.c_void_p),
        ("len", ctypes.c_size_t),
    ]

    def __repr__(self) -> str:
        return f"GenericSlice(len={self.len}, ptr={self.ptr})"

    def to_list(self, ctype: type, encoding="utf-8") -> List:
        """Return the slice as a Python list.

        If `ctype` is `PyString`, the entire underlying byte array is decoded into
        a single Python string and returned as a list with one element.
        For other ctypes, the slice is returned as a list of individual instances.

        May raise a EOFError if the slice is empty."""
        if self.is_empty:
            raise EOFError("Slice is empty.")
        if ctype is PyString:
            buf = bytes((ctypes.c_char * self.len).from_address(self.ptr))
            return [buf.decode(encoding)]

        ptr = ctypes.cast(self.ptr, ctypes.POINTER(ctype))
        return [ptr[i] for i in range(self.len)]

    @property
    def is_empty(self) -> bool:
        """Whether the slice is empty."""
        return self.ptr is None


class ASTNode(ctypes.Structure):
    """Represents a node in the Zig AST."""

    _fields_ = [
        ("index", ctypes.c_int),
        ("tag_index", ctypes.c_int),
        ("main_token", ctypes.c_int),
        ("lhs", ctypes.c_int),
        ("rhs", ctypes.c_int),
    ]

    def __repr__(self) -> str:
        return (
            f"ASTNode("
            f"tag={self.tag}, "
            f"index={self.index}, "
            f"main_token={self.main_token}, "
            f"lhs={self.lhs}, "
            f"rhs={self.rhs})"
        )

    @property
    def tag(self) -> NodeTag:
        """The node tag as a `NodeTag` enum."""
        return NodeTag(self.tag_index)


class ASTToken(ctypes.Structure):
    """Represents a token in the Zig AST."""

    _fields_ = [
        ("tag_index", ctypes.c_int),
        ("start", ctypes.c_int),
    ]

    def __repr__(self) -> str:
        return f"ASTToken(tag={self.tag}, start={self.start})"

    @property
    def tag(self) -> TokenTag:
        """The token tag as a `TokenTag` enum."""
        return TokenTag(self.tag_index)


class ErrorReport(ctypes.Structure):
    """Represents a parsing error."""

    _fields_ = [
        ("tag_index", ctypes.c_int),
        ("is_note", ctypes.c_bool),
        ("token_is_prev", ctypes.c_bool),
        ("token_index", ctypes.c_int),
    ]

    def __repr__(self) -> str:
        return (
            f"ErrorData("
            f"tag={self.tag}, "
            f"is_note={self.is_note}, "
            f"token_is_prev={self.token_is_prev}, "
            f"token_index={self.token_index})"
        )

    @property
    def tag(self) -> ErrorTag:
        """The error tag as an `ErrorTag` enum."""
        return ErrorTag(self.tag_index)


class NodeParam(ctypes.Structure):
    """Represents a node parameter."""

    _fields_ = [
        ("name", GenericSlice),
        ("type", ASTNode)
    ]

    def __repr__(self) -> str:
        return f"NodeParam(name={self.name}, type={self.type})"
