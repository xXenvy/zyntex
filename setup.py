from typing import cast

import subprocess
import sys

from setuptools import Command, setup, find_packages
from setuptools.command.build_py import build_py as _build_py
from pathlib import Path

from zyntex import __version__


class build_py(_build_py):
    def run(self):
        subprocess.check_call([sys.executable, "build_libs.py", "--release-mode"])
        super().run()


here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8") \
    if (here / "README.md").exists() else ""

setup(
    name="zyntex",
    version=str(__version__),
    description="A high-level Python package to parse Zig code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="xXenvy",
    url="https://github.com/xXenvy/zyra",
    project_urls={
        "Source": "https://github.com/xXenvy/zyntex",
        "Tracker": "https://github.com/xXenvy/zyntex/issues",
    },
    license="MIT",
    packages=find_packages(exclude=("tests", "zig")),
    include_package_data=True,
    package_data={"zyntex": ["bindings/native/*"]},
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
    cmdclass={"build_py": cast(type[Command], build_py)},
)
