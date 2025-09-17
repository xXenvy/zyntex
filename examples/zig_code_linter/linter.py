"""
Minimal, pluggable Zig AST linter, build with zyntex.
"""
from zyntex.parsing.syntax import INodeElement
from zyntex.parsing import SourceFile, SourceModule

from typing import Literal, Callable
from dataclasses import dataclass
from pathlib import Path

IssueLevel = Literal["warning", "error"]


@dataclass
class Issue:
    """Represents a single linter finding."""
    level: IssueLevel
    file: str
    line: int
    message: str


RuleCallable = Callable[[INodeElement, SourceFile], list[Issue]]


@dataclass
class Rule:
    """
    A linter rule describing which AST node types the rule applies to
    and the callable implementing the check.

    The rule's callback must follow the `RuleCallable` signature:
        (node: INodeElement, file: SourceFile) -> list[Issue]
    """
    targets: tuple[type[INodeElement], ...]
    callback: RuleCallable


class ZigCodeLinter:
    """Linter class that holds and runs rules against files / directories."""

    def __init__(self) -> None:
        self._rules: list[Rule] = []

    def register_rule(self, rule: Rule) -> None:
        self._rules.append(rule)

    def run(self, path: str) -> list[Issue]:
        """Run the linter over `path` (file or directory).

        Returns a list of Issue objects. Raises FileNotFoundError if path doesn't exist."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Path '{p}' does not exist. "
                                    f"Provide a valid path to .zig file or directory.")

        files = [SourceFile(str(p))] if p.is_file() else SourceModule(str(p)).files
        issues: list[Issue] = []

        for file in files:
            for content in file.content:
                for rule_callback in self._applicable_rules_for_node(content):
                    issues.extend(rule_callback(content, file))
        return issues

    def _applicable_rules_for_node(self, node: INodeElement) -> list[RuleCallable]:
        result: list[RuleCallable] = []
        for rule in self._rules:
            if any(isinstance(node, t) for t in rule.targets):
                result.append(rule.callback)
        return result

    @staticmethod
    def pretty_print(issues: list[Issue]) -> None:
        """Print linter issues in a compact form."""
        if not issues:
            print("No issues found 🎉")
            return

        total = 0
        errors = 0
        files_set = set()

        for issue in issues:
            total += 1
            files_set.add(issue.file)
            if issue.level.lower() == "error":
                errors += 1

            print(f"{issue.file}:{issue.line} [{issue.level}] {issue.message}")

        warnings = total - errors
        files_count = len(files_set)

        print(f"""-----------------------
Found {total} issues ({errors} errors, {warnings} warnings) in {files_count} files.""")
