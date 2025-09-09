from typing import Type, cast

from ...syntax.type_node import TypeNode
from ..printer import PrinterDispatcher
from .default_printer import IDefaultPrintable


class TypePrinter(IDefaultPrintable):
    """Printer for Zig type nodes."""

    def __init__(
            self,
            dispatcher: PrinterDispatcher,
    ):
        self._dispatcher = dispatcher

    def print(self, target: TypeNode) -> str:
        result = ""
        current: TypeNode = target
        while True:
            if current.is_type():
                if current.const:
                    result += "const "
                result += current.type.value
                break
            if current.is_optional():
                result += "?"
                current = cast(TypeNode, current.optional_type)
                continue
            if current.is_pointer():
                result += "*"
                current = cast(TypeNode, current.pointer_type)
                continue
            if current.is_array():
                assert current.array_length, f"Array type ({current!r}) has no array_length."
                result += f"[{current.array_length}]"
                current = cast(TypeNode, current.array_type)
                continue
        return result

    @staticmethod
    def target_type() -> Type[TypeNode]:
        return TypeNode
