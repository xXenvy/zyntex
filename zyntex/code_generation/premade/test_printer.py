from typing import Type

from ...syntax import TestDeclaration
from ..printer import PrinterDispatcher
from .default_printer import IDefaultPrintable


class TestPrinter(IDefaultPrintable):
    """Printer for Zig test declarations."""

    def __init__(
            self,
            dispatcher: PrinterDispatcher,
    ):
        self._dispatcher = dispatcher

    def print(self, target: TestDeclaration) -> str:
        if target.name is None:
            return f"test {target.body}"
        return f"test {target.name} {target.body}"

    @staticmethod
    def target_type() -> Type[TestDeclaration]:
        return TestDeclaration
