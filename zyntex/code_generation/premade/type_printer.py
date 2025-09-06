from typing import Type, cast

from ...syntax.type_node import TypeNode
from ..printer import PrinterDispatcher
from .default_printer import IDefaultPrintable


class TypePrinter(IDefaultPrintable):
    """Printer for Zig type nodes."""

    def __init__(self, dispatcher: PrinterDispatcher):
        self._dispatcher = dispatcher

    def print(self, target: TypeNode) -> str:
        result = ""
        current: TypeNode = target
        while True:
            if current.is_type():
                if current.is_const():
                    result += "const "
                result += current.spelling
                break
            if current.is_optional():
                result += "?"
                current = cast(TypeNode, current.optional_type)
                continue
            if current.is_ptr():
                result += "*"
                current = cast(TypeNode, current.ptr_type)
                continue
            if current.is_array():
                result += f"[{current.array_length}]"
                current = cast(TypeNode, current.array_type)
                continue
        return result

    @staticmethod
    def target_type() -> Type[TypeNode]:
        return TypeNode
