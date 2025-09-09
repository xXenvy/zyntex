from abc import ABC, abstractmethod
from typing import Dict, Type, Any

from .configuration import PrinterConfiguration


class IPrinter(ABC):
    """Base interface for all printers.

    Each printer must accept a dispatcher in its constructor
    and implement `print(target)` to return code for a node."""

    @abstractmethod
    def __init__(
            self,
            dispatcher: "PrinterDispatcher",
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def print(self, target: Any) -> str:
        """Produced output of the printer."""
        raise NotImplementedError


class PrinterDispatcher:
    """Collects printers and chooses the right one for each node.

    You can register printers with `add`, remove them with `remove`,
    and use `print` to get code for any supported node."""

    def __init__(self, configuration: PrinterConfiguration = PrinterConfiguration()) -> None:
        self.configuration = configuration
        self._printers: Dict[Type, IPrinter] = {}

    def add(self, target_type: Type, target_printer_type: Type[IPrinter]) -> None:
        """Register a printer for the given node type."""
        self._printers[target_type] = target_printer_type(self)

    def remove(self, target_type: Type) -> None:
        """Unregister the printer for the given node type."""
        del self._printers[target_type]

    def print(self, target: Any) -> str:
        """Produces source code for the given AST node."""
        target_type = type(target)
        if printer := self._printers.get(target_type):
            return printer.print(target)
        raise KeyError(f"No printer registered for node: {target}.")
