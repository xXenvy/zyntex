from dataclasses import dataclass

from .source_file import SourceFile
from .source_module import SourceModule
from .source_code import SourceCode


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


__all__ = (
    "SourceFile",
    "SourceModule",
    "SourceCode",
    "__version__"
)

__version__ = Version(0, 0, 3)
