from concurrent.futures import ThreadPoolExecutor
from os import walk, path, cpu_count

from typing import Optional

from .bindings import init_native_library
from .source_file import SourceFile


class SourceModule:
    """Container that discovers and parses .zig files under a directory.

    Parameters
    ----------
    dir_path:
        Directory to search for `.zig` files.

    lazy_parsing:
        Controls whether parsing is deferred. When enabled, constructing a
        :class:`SourceFile` is cheap and actual parsing happens later when the
        file's content/unit is accessed. When disabled, parsing is performed
        eagerly during construction.

        .. versionadded:: 0.2.3

    use_threading:
        Controls whether parsing work is submitted to a thread pool.
        Using threads can significantly speed up parsing when there are many
        files, because parsing and native calls can run concurrently.

        .. versionadded:: 0.2.3

    max_workers:
        Upper bound on the number of worker threads when threading is used.
        If None, picks a sensible default based on CPU count and number of
        files.

        .. versionadded:: 0.2.3
    """

    def __init__(
            self,
            dir_path: str,
            lazy_parsing: bool = False,
            use_threading: bool = False,
            max_workers: Optional[int] = None,
    ) -> None:
        self.lazy_parsing = lazy_parsing
        self.use_threading = use_threading
        self.max_workers = None if max_workers is None else max_workers

        self._dir_path = dir_path

    def __repr__(self) -> str:
        return (
            f"SourceModule(dir={self._dir_path}, use_threading={self.use_threading}, "
            f"max_workers={self.max_workers}, lazy_parsing={self.lazy_parsing})"
        )

    @property
    def files(self) -> list[SourceFile]:
        """A list of SourceFile objects for every .zig file under ``dir_path``."""
        paths: list[str] = []
        for root, _, files in walk(self._dir_path):
            for filename in files:
                if filename.endswith(".zig"):
                    full_path = path.join(root, filename)
                    paths.append(full_path)

        if not paths:
            return []

        # Sequential parsing path: simple and predictable
        if not self.use_threading:
            return [SourceFile(p, lazy_parsing=self.lazy_parsing) for p in paths]

        # Decide number of workers; explicit setting wins,
        # otherwise compute a reasonable default.
        max_workers = self.max_workers or min(len(paths), cpu_count() or 4)

        # Ensure native library is initialised before spawning workers to avoid
        # races during library load or global init.
        init_native_library()

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            sources = list(ex.map(lambda p: SourceFile(p, lazy_parsing=self.lazy_parsing), paths))
        return sources

    @property
    def dir_path(self) -> str:
        """Path that this SourceModule will walk for .zig files."""
        return self._dir_path
