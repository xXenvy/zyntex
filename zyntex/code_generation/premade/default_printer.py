from abc import ABC, abstractmethod
from typing import Type, Any

from ..printer import IPrinter, PrinterDispatcher


class IDefaultPrintable(IPrinter, ABC):
    """Base for printers that register themselves automatically.

    Subclasses must define `target_type()` and will be added to the
    shared dispatcher."""
    dispatcher = PrinterDispatcher()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "__abstractmethods__", False):
            IDefaultPrintable.dispatcher.add(cls.target_type(), cls)

    @staticmethod
    @abstractmethod
    def target_type() -> Type:
        """The NodeElement this printer handles."""
        raise NotImplementedError


class DefaultCodePrinter(IPrinter):
    """Printer that combines all default printers into one."""

    def __init__(self, dispatcher: PrinterDispatcher = IDefaultPrintable.dispatcher) -> None:
        self.dispatcher = dispatcher

    def print(self, target: Any) -> str:
        return self.dispatcher.print(target)
