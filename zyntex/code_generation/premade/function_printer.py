from typing import Type

from ...syntax import FunctionDeclaration
from ..printer import PrinterDispatcher
from .default_printer import IDefaultPrintable


class FunctionPrinter(IDefaultPrintable):
    """Printer for Zig function declarations."""

    def __init__(
            self,
            dispatcher: PrinterDispatcher,
    ):
        self._dispatcher = dispatcher

    def print(self, target: FunctionDeclaration) -> str:
        modifiers = "".join(
            mod for condition, mod in (
                (target.is_public, "pub "),
                (target.is_extern, "extern "),
                (not target.is_extern and target.is_export, "export "),
            ) if condition
        )
        args = ", ".join(
            f"{param.name}: {self._dispatcher.print(param.type)}" for param in target.params
        )
        return_type = self._dispatcher.print(target.return_type)
        body = f" {target.body}" if target.body is not None else ";"
        return f"{modifiers}fn {target.name}({args}) {return_type}{body}"

    @staticmethod
    def target_type() -> Type[FunctionDeclaration]:
        return FunctionDeclaration
