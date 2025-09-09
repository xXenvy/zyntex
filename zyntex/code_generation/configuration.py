from dataclasses import dataclass


@dataclass
class PrinterConfiguration:
    """Printer formatting options.

    Attributes:
        line_ending: String used to join/terminate printed elements (e.g. "\n\n").
    """
    line_ending: str = "\n\n"
