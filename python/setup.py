import runpy
import subprocess
import sys
from pathlib import Path
from typing import cast

from setuptools import Command, setup, find_packages
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist

here = Path(__file__).resolve().parent
repository_root = here.parent if (here.parent / "zig" / "build.zig").is_file() else here
version = runpy.run_path(str(here / "src" / "__init__.py"))["__version__"]


class build_py(_build_py):
    def run(self):
        subprocess.check_call([
            sys.executable,
            str(repository_root / "tools" / "build_libs.py"),
            "--release-mode",
        ])
        super().run()


class sdist(_sdist):
    def check_readme(self):
        if not (repository_root / "README.md").is_file():
            super().check_readme()

    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        # Source archives also need the native build sources from the repository.
        resources = [
            repository_root / "README.md",
            repository_root / "LICENSE",
            repository_root / "tools" / "build_libs.py",
            *sorted((repository_root / "zig").glob("*.zig")),
            *sorted((repository_root / "zig").glob("*.zon")),
        ]
        for directory in ("src", "tests", "tools"):
            resources.extend(sorted((repository_root / "zig" / directory).rglob("*.zig")))
        for source in resources:
            destination = Path(base_dir) / source.relative_to(repository_root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            self.copy_file(str(source), str(destination))

        manifest = Path(base_dir) / self.get_finalized_command("egg_info").egg_info / "SOURCES.txt"
        with manifest.open("a", encoding="utf-8") as stream:
            for source in resources:
                stream.write(source.relative_to(repository_root).as_posix() + "\n")


long_description = (repository_root / "README.md").read_text(encoding="utf-8")

setup(
    name="zyntex",
    version=str(version),
    description="A high-level Python package to parse and generate Zig code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="xXenvy",
    url="https://github.com/xXenvy/zyntex",
    project_urls={
        "Source": "https://github.com/xXenvy/zyntex",
        "Tracker": "https://github.com/xXenvy/zyntex/issues",
    },
    license="MIT",
    package_dir={"zyntex": "src"},
    packages=["zyntex"] + [f"zyntex.{name}" for name in find_packages(where="src")],
    include_package_data=True,
    package_data={"zyntex": ["parsing/bindings/native/*"]},
    python_requires=">=3.9",
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="zig parser codegen",
    zip_safe=False,
    cmdclass={
        "build_py": cast(type[Command], build_py),
        "sdist": cast(type[Command], sdist),
    },
)
