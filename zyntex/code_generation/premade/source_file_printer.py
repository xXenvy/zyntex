from typing import Type

from ...source_file import SourceFile
from ..printer import PrinterDispatcher
from .default_printer import IDefaultPrintable


class SourceFilePrinter(IDefaultPrintable):
    """Printer for Zig source file."""

    def __init__(
            self,
            dispatcher: PrinterDispatcher,
    ):
        self._dispatcher = dispatcher

    def print(self, target: SourceFile) -> str:
        return f"{self._dispatcher.configuration.line_ending}".join(
            self._dispatcher.print(content) for content in target.content
        )

    @staticmethod
    def target_type() -> Type[SourceFile]:
        return SourceFile
