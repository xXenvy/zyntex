from abc import ABC, abstractmethod
from typing import Any, Optional

from .configuration import PrinterConfiguration


class IPrinter(ABC):
    """Base interface for all printers.

    Each printer receives a dispatcher in its constructor and must implement
    `print(target)` to produce the output for a node."""

    def __init__(self, dispatcher: "PrinterDispatcher") -> None:
        self._dispatcher = dispatcher

    @abstractmethod
    def print(self, target: Any) -> str:
        """Produced output of the printer."""


class PrinterDispatcher:
    """Collects printers and chooses the right one for each node.

    You can register printers with `add`, remove them with `remove`,
    and use `print` to get code for any supported node."""

    def __init__(self, configuration: Optional[PrinterConfiguration] = None) -> None:
        self.configuration = configuration or PrinterConfiguration()
        self._printers: dict[type, IPrinter] = {}

    def add(self, target_type: type, target_printer_type: type[IPrinter]) -> None:
        """Register a printer for the given node type."""
        self._printers[target_type] = target_printer_type(self)

    def remove(self, target_type: type) -> None:
        """Unregister the printer for the given node type."""
        del self._printers[target_type]

    def print(self, target: Any) -> str:
        """Produces source code for the given AST node."""
        target_type = type(target)
        if printer := self._printers.get(target_type):
            return printer.print(target)
        raise KeyError(f"No printer registered for node: {target}.")
