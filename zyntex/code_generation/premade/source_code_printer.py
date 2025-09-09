from typing import Type

from ...source_code import SourceCode
from ..printer import PrinterDispatcher
from .default_printer import IDefaultPrintable


class SourceCodePrinter(IDefaultPrintable):
    """Printer for Zig source code."""

    def __init__(
            self,
            dispatcher: PrinterDispatcher,
    ):
        self._dispatcher = dispatcher

    def print(self, target: SourceCode) -> str:
        return f"{self.dispatcher.configuration.line_ending}".join(
            self._dispatcher.print(content) for content in target.content
        )

    @staticmethod
    def target_type() -> Type[SourceCode]:
        return SourceCode
