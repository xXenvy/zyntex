import subprocess
import os
import sys
import logging

from argparse import ArgumentParser, Namespace
from pathlib import Path
from shutil import rmtree

logger = logging.getLogger(__name__)
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def check_sphinx() -> str:
    try:
        p = subprocess.run(["sphinx-build", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError("sphinx-build not found in PATH. Install Sphinx (pip install sphinx).")
    if p.returncode != 0:
        raise RuntimeError(f"'sphinx-build --version' failed: {(p.stderr or p.stdout).strip()}")
    return (p.stdout or p.stderr).strip()


def install_requirements(requirements_path: str) -> None:
    if not os.path.exists(requirements_path):
        logger.info("Requirements file not found: %s — skipping install.", requirements_path)
        return

    cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_path]
    logger.info("Installing docs requirements: %s", " ".join(cmd))
    p = subprocess.run(cmd, capture_output=True, text=True)

    if p.returncode != 0:
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        raise RuntimeError(f"Failed to install requirements from {requirements_path}.\n"
                           f"stdout: {out}\nstderr: {err}")
    logger.info("Requirements installed successfully.")


def build_docs(source: str, build_dir: str) -> None:
    os.makedirs(build_dir, exist_ok=True)
    cmd = ["sphinx-build", "-b", "html", source, build_dir]

    logger.info("Running: %s", " ".join(cmd))
    p = subprocess.run(cmd)

    if p.returncode != 0:
        raise RuntimeError(f"Sphinx build failed (exit {p.returncode}).")
    logger.info("Build finished: %s", build_dir)


def parse_args() -> Namespace:
    p = ArgumentParser(description="Build sphinx docs locally.")
    p.add_argument(
        "--clean",
        action="store_true",
        help="Remove build dir before building."
    )
    p.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip installing requirements before build."
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    if not args.skip_install:
        install_requirements(str(REPOSITORY_ROOT / "docs" / "requirements.txt"))

    ver = check_sphinx()
    logger.info("Found: %s", ver)

    source_dir = REPOSITORY_ROOT / "docs"
    build_dir = source_dir / "_build" / "html"
    if args.clean and build_dir.exists():
        logger.info("Cleaning: %s", build_dir)
        rmtree(build_dir)

    build_docs(str(source_dir), str(build_dir))
    logger.info("Done.")


if __name__ == "__main__":
    assert sys.version_info >= (3, 11), "This script requires Python 3.11 or newer."
    main()
