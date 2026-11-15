from ...parsing.source_file import SourceFile
from .default_printer import IDefaultPrintable


class SourceFilePrinter(IDefaultPrintable):
    """Printer for Zig source file."""

    def print(self, target: SourceFile) -> str:
        return f"{self._dispatcher.configuration.line_ending}".join(
            self._dispatcher.print(content) for content in target.content
        )

    @staticmethod
    def target_type() -> type[SourceFile]:
        return SourceFile
