from abc import ABC, abstractmethod
from typing import Any

from ..printer import IPrinter, PrinterDispatcher


class IDefaultPrintable(IPrinter, ABC):
    """Base for printers that register themselves automatically.

    Subclasses must define `target_type()` and will be added to the
    shared dispatcher."""
    default_dispatcher = PrinterDispatcher()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "__abstractmethods__", False):
            IDefaultPrintable.default_dispatcher.add(cls.target_type(), cls)

    @staticmethod
    @abstractmethod
    def target_type() -> type:
        """The NodeElement this printer handles."""


class DefaultCodePrinter(IPrinter):
    """Printer that combines all default printers into one."""

    def __init__(self) -> None:
        super().__init__(IDefaultPrintable.default_dispatcher)

    def print(self, target: Any) -> str:
        return self._dispatcher.print(target)
