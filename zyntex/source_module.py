from typing import List
from os import walk, path

from .source_file import SourceFile


class SourceModule:
    """A SourceModule, which allows you to parse multiple .zig files.
    From the provided path, all .zig files will be extracted."""

    __slots__ = ("_dir_path",)

    def __init__(self, dir_path: str) -> None:
        self._dir_path = dir_path

    def __repr__(self) -> str:
        return f"SourceModule(dir={self._dir_path})"

    @property
    def files(self) -> List[SourceFile]:
        """A list of SourceFile for all `.zig` files in the directory."""
        sources = []
        for root, _, files in walk(self._dir_path):
            for filename in files:
                if filename.endswith(".zig"):
                    full_path = path.join(root, filename)
                    sources.append(SourceFile(full_path))
        return sources

    @property
    def dir_path(self) -> str:
        """Provided path to the directory."""
        return self._dir_path
