from ...parsing.syntax import VariableDeclaration
from .default_printer import IDefaultPrintable


class VariablePrinter(IDefaultPrintable):
    """Printer for Zig variable declarations."""

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
        annotation = target.type_hint
        type_hint = f": {annotation}" if annotation is not None else ""
        if target.is_extern or target.value is None:
            return f"{modifiers}{target.name}{type_hint};"
        return f"{modifiers}{target.name}{type_hint} = {target.value};"

    @staticmethod
    def target_type() -> type[VariableDeclaration]:
        return VariableDeclaration
