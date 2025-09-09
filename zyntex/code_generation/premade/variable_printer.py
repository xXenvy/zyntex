from typing import Type

from ...syntax import VariableDeclaration
from ..printer import PrinterDispatcher
from .default_printer import IDefaultPrintable


class VariablePrinter(IDefaultPrintable):
    """Printer for Zig variable declarations."""

    def __init__(
            self,
            dispatcher: PrinterDispatcher,
    ):
        self._dispatcher = dispatcher

    def print(self, target: VariableDeclaration) -> str:
        modifiers = "".join(
            mod for condition, mod in (
                (target.is_public, "pub "),
                (target.is_extern, "extern "),
                (not target.is_extern and target.is_export, "export "),
                (target.is_const, "const "),
                (not target.is_const, "var "),
            ) if condition
        )
        type_hint = ""
        if target.type_hint:
            type_hint = f": {self._dispatcher.print(target.type_hint)}"
        if target.is_extern:
            return f"{modifiers}{target.name}{type_hint};"
        return f"{modifiers}{target.name}{type_hint} = {target.value};"

    @staticmethod
    def target_type() -> Type[VariableDeclaration]:
        return VariableDeclaration
