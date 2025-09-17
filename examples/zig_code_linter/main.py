"""
Simple Zig code linter implemented using zyntex.
"""
import argparse
import re

from zyntex.parsing.syntax import INodeElement, FunctionDeclaration
from zyntex.parsing import SourceFile

from linter import ZigCodeLinter, Issue, Rule, RuleCallable, IssueLevel


def _find_line_of_decl(file: SourceFile, pattern: str) -> int:
    """Helper for approximating the line number of a node declaration.

    Since Zyntex currently exposes a limited API and does not provide
    direct access to node source locations."""
    source_text = file.unit.source
    match = re.search(pattern, source_text)
    if not match:
        return -1  # not found
    return source_text[:match.start()].count("\n") + 1


def make_func_name_rule(pattern: str, level: IssueLevel) -> RuleCallable:
    compiled = re.compile(pattern)

    def rule(node: INodeElement, file: SourceFile) -> list[Issue]:
        issues: list[Issue] = []

        # Only interested in function declarations
        if not isinstance(node, FunctionDeclaration):
            return issues

        name = node.name
        if compiled.match(name):
            return issues

        # Approximate line number
        line = _find_line_of_decl(file, rf"\bfn\s+{re.escape(name)}\b")
        issues.append(
            Issue(
                level=level,
                file=file.path,
                line=line,
                message=f"Invalid function name: '{name}' (does not match pattern: {pattern})"
            )
        )
        return issues

    return rule


def make_func_max_params_rule(max_params: int, level: IssueLevel) -> RuleCallable:
    def rule(node: INodeElement, file: SourceFile) -> list[Issue]:
        issues: list[Issue] = []

        # Only interested in function declarations
        if not isinstance(node, FunctionDeclaration):
            return issues

        # Defensive access to params.
        # Zyntex may raise AssertionError if a parameter has an
        # unsupported type (e.g., a struct type). In that case we
        # simply skip this function. Future versions of Zyntex
        # should provide full type support and make this unnecessary.
        try:
            params = node.params
        except AssertionError:
            return issues

        if len(params) <= max_params:
            return issues

        # Approximate line number
        line = _find_line_of_decl(file, rf"\bfn\s+{re.escape(node.name)}\b")
        issues.append(
            Issue(
                level=level,
                file=file.path,
                line=line,
                message=(
                    f"Function '{node.name}' has too many params: {len(params)} "
                    f"(max: {max_params})"
                )
            )
        )
        return issues

    return rule


def build_linter(
        max_params: int,
        name_pattern: str,
) -> ZigCodeLinter:
    """Helper to configure the linter with two example rules."""
    linter = ZigCodeLinter()

    # Create rule objects
    max_params_rule = Rule(
        targets=(FunctionDeclaration,),
        callback=make_func_max_params_rule(max_params, "warning"),
    )
    func_name_rule = Rule(
        targets=(FunctionDeclaration,),
        callback=make_func_name_rule(name_pattern, "warning"),
    )
    linter.register_rule(max_params_rule)
    linter.register_rule(func_name_rule)
    return linter


def main() -> None:
    parser = argparse.ArgumentParser(description="Example Zig linter.")
    parser.add_argument("path", help="Zig file or directory to lint")
    parser.add_argument("--max-params", type=int, default=6, help="Max allowed function parameters")
    parser.add_argument(
        "--name-pattern",
        default=r"^[a-z][a-z0-9_]*$",
        help="Regex for valid function names (default: permissive snake_case)"
    )
    args = parser.parse_args()

    linter = build_linter(args.max_params, args.name_pattern)
    found_issues: list[Issue] = linter.run(args.path)
    ZigCodeLinter.pretty_print(found_issues)


if __name__ == "__main__":
    main()
