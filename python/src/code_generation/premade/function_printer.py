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
        args = ", ".join(self._dispatcher.print(param) for param in target.params)
        body = f" {target.body}" if target.body is not None else ";"
        return f"{modifiers}fn {target.name}({args}) {target.return_type}{body}"

    @staticmethod
    def target_type() -> type[FunctionDeclaration]:
        return FunctionDeclaration


class FunctionParamPrinter(IDefaultPrintable):
    """Printer for Zig function parameters."""

    def print(self, target: FunctionDeclaration.FunctionParam) -> str:
        modifier = "comptime " if target.is_comptime else "noalias " if target.is_noalias else ""
        name = f"{target.name}: " if target.name is not None else ""
        return f"{modifier}{name}{target.type}"

    @staticmethod
    def target_type() -> type[FunctionDeclaration.FunctionParam]:
        return FunctionDeclaration.FunctionParam
