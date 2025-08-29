import ctypes
import os

from dataclasses import dataclass
from typing import Optional, Tuple

from .structures import ASTNode, GenericSlice, NodeParam
from .translation_unit import TranslationUnitPtr

_lib_instance: Optional[ctypes.CDLL] = None


@dataclass
class FunctionSignature:
    name: str
    return_type: Optional[type]
    arg_types: Tuple[type, ...]


lib_functions = [
    FunctionSignature("createTranslationUnit", TranslationUnitPtr, (ctypes.c_char_p,)),
    FunctionSignature("createTranslationUnitFromSource", TranslationUnitPtr, (ctypes.c_char_p,)),
    FunctionSignature("getTranslationUnitNodesCount", ctypes.c_size_t, (TranslationUnitPtr,)),
    FunctionSignature("getTranslationUnitNodes", GenericSlice, (TranslationUnitPtr,)),
    FunctionSignature("getTranslationUnitRootNodes", GenericSlice, (TranslationUnitPtr,)),
    FunctionSignature("getTranslationUnitNodeFromIndex", ASTNode,
                      (TranslationUnitPtr, ctypes.c_uint32)),
    FunctionSignature("getTranslationUnitTokensCount", ctypes.c_size_t, (TranslationUnitPtr,)),
    FunctionSignature("getTranslationUnitTokens", GenericSlice, (TranslationUnitPtr,)),
    FunctionSignature("getTranslationUnitErrorsCount", ctypes.c_size_t, (TranslationUnitPtr,)),
    FunctionSignature("getTranslationUnitErrors", GenericSlice, (TranslationUnitPtr,)),
    FunctionSignature("getTranslationUnitSource", GenericSlice, (TranslationUnitPtr,)),
    FunctionSignature("freeTranslationUnit", None, (TranslationUnitPtr,)),

    FunctionSignature("getNodeSpelling", GenericSlice, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("getNodeSource", GenericSlice, (TranslationUnitPtr, ctypes.c_uint32)),
    FunctionSignature("getNodeType", ASTNode, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("getNodeAlign", GenericSlice, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("getNodeBody", GenericSlice, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("getNodeParamsCount", ctypes.c_size_t, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("getNodeParams", ctypes.c_size_t,
                      (TranslationUnitPtr, ASTNode, ctypes.POINTER(NodeParam), ctypes.c_size_t)),
    FunctionSignature("isNodeExtern", ctypes.c_bool, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("isNodeExport", ctypes.c_bool, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("isNodePublic", ctypes.c_bool, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("isNodeConst", ctypes.c_bool, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("isNodeContainer", ctypes.c_bool, (ASTNode,)),
    FunctionSignature("isNodeStruct", ctypes.c_bool, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("isNodeUnion", ctypes.c_bool, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("isNodeOpaque", ctypes.c_bool, (TranslationUnitPtr, ASTNode)),
    FunctionSignature("isNodeEnum", ctypes.c_bool, (TranslationUnitPtr, ASTNode)),
]


def get_lib_ext() -> str:
    from sys import platform  # pylint: disable=import-outside-toplevel

    exts = {"win32": "dll", "darwin": "dylib", "linux": "so"}
    if ext := exts.get(platform):
        return ext
    raise ValueError(f"Invalid platform: '{platform}'.")


def load_native_library(lib_dir: Optional[str] = None) -> ctypes.CDLL:
    lib_ext: str = get_lib_ext()
    path = lib_dir or os.path.join(os.path.dirname(os.path.realpath(__file__)), "native")
    ctypes_lib = ctypes.CDLL(f"{path}/clib.{lib_ext}")

    for func in lib_functions:
        lib_func = getattr(ctypes_lib, func.name)
        setattr(lib_func, "argtypes", func.arg_types)
        setattr(lib_func, "restype", func.return_type)
    return ctypes_lib


def get_native_library(lib_dir: Optional[str] = None) -> ctypes.CDLL:
    global _lib_instance  # pylint: disable=global-statement
    if _lib_instance is None:
        _lib_instance = load_native_library(lib_dir)
    return _lib_instance
