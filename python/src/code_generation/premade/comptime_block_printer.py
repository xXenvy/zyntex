from ...parsing.syntax import ComptimeBlock
from .default_printer import IDefaultPrintable


class ComptimeBlockPrinter(IDefaultPrintable):
    """Printer for Zig comptime blocks.

    .. versionadded:: 0.3.3
    """

    def print(self, target: ComptimeBlock) -> str:
        return f"comptime {target.body}"

    @staticmethod
    def target_type() -> type[ComptimeBlock]:
        return ComptimeBlock
