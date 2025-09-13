from ...parsing.syntax import TestDeclaration
from .default_printer import IDefaultPrintable


class TestPrinter(IDefaultPrintable):
    """Printer for Zig test declarations."""

    def print(self, target: TestDeclaration) -> str:
        if target.name is None:
            return f"test {target.body}"
        return f"test {target.name} {target.body}"

    @staticmethod
    def target_type() -> type[TestDeclaration]:
        return TestDeclaration
