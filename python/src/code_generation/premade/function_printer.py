from ...parsing.syntax import FunctionDeclaration
from .default_printer import IDefaultPrintable


class FunctionPrinter(IDefaultPrintable):
    """Printer for Zig function declarations."""

    def print(self, target: FunctionDeclaration) -> str:
        modifiers = "".join(
            mod for condition, mod in (
                (target.is_public, "pub "),
                (target.is_extern, "extern "),
                (not target.is_extern and target.is_export, "export "),
            ) if condition
        )
        args = ", ".join(
            f"{'comptime ' if param.is_comptime else ''}{param.name}: "
            f"{self._dispatcher.print(param.type)}"
            for param in target.params
        )
        return_type = self._dispatcher.print(target.return_type)
        body = f" {target.body}" if target.body is not None else ";"
        return f"{modifiers}fn {target.name}({args}) {return_type}{body}"

    @staticmethod
    def target_type() -> type[FunctionDeclaration]:
        return FunctionDeclaration
