import subprocess
import os
import logging

from argparse import ArgumentParser, Namespace
from pathlib import Path
from shutil import copy2, rmtree

logger = logging.getLogger(__name__)
ZIG_VERSION = "0.17.1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = REPOSITORY_ROOT / "python" if (REPOSITORY_ROOT / "python" / "setup.py").is_file() else REPOSITORY_ROOT


def check_zig_version() -> str:
    try:
        result = subprocess.run(["zig", "version"], capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError(
            f"Zig {ZIG_VERSION} is required to build the native libraries, "
            "but Zig is not installed or not found in PATH. "
            f"Install Zig {ZIG_VERSION}, add its executable directory to PATH, "
            "and verify the installation with 'zig version'."
        )

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(
            f"'zig version' failed (return code: {result.returncode}). "
            f"Stderr: {stderr}."
        )

    version = (result.stdout or "").strip()
    logger.info("Found Zig version: %s", version)
    if version != ZIG_VERSION:
        raise RuntimeError(f"Zig {ZIG_VERSION} is required; found {version!r}.")
    return version


def run_build(release_mode: bool, out_dir: str) -> None:
    args = ["zig", "build", "install", "--summary", "all", "--prefix", out_dir]
    if release_mode:
        args.append("-Doptimize=ReleaseFast")

    logger.info("Running: %s", " ".join(args))
    result = subprocess.run(args, cwd=REPOSITORY_ROOT / "zig")
    if result.returncode != 0:
        raise RuntimeError(f"Zig build failed ({result.returncode}).")
    logger.info("Zig build completed successfully.")


def copy_and_rename_libs(out_dir: str, dest_dir: str) -> None:
    logger.info("Copying libraries from '%s' to '%s'", out_dir, dest_dir)

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    lib_subdir = {"dll": "bin", "so": "lib", "dylib": "lib"}

    copied_any = False
    for ext, sub in lib_subdir.items():
        search_dir = os.path.join(out_dir, sub)
        if not os.path.exists(search_dir):
            logger.debug("Directory not found: %s", search_dir)
            continue

        for filename in os.listdir(search_dir):
            if filename.endswith(f".{ext}"):
                src_path = os.path.join(search_dir, filename)
                dest_path = os.path.join(dest_dir, f"clib.{ext}")
                logger.info("Copying %s -> %s", src_path, dest_path)
                copy2(src_path, dest_path)
                copied_any = True

    if not copied_any:
        logger.warning("No libraries found to copy in %s", out_dir)


def cleanup(*dirs) -> None:
    for path in dirs:
        if os.path.exists(path):
            logger.info("Removing: %s", path)
            rmtree(path)
        else:
            logger.debug("Skipped (does not exist): %s", path)


def parse_args() -> Namespace:
    p = ArgumentParser()
    p.add_argument("--release-mode", action="store_true", help="Build libs in release mode.")
    p.add_argument(
        "--out-dir",
        default=str(REPOSITORY_ROOT / "zig" / "zig-out"),
        help="Build output directory.",
    )
    p.add_argument(
        "--dest-dir",
        default=str(PYTHON_ROOT / "src" / "parsing" / "bindings" / "native"),
        help="Destination directory for native libs."
    )
    p.add_argument("--keep-cache", action="store_true", help="Do not delete zig cache dir.")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(message)s"
    )
    check_zig_version()
    logger.info("The zig version is correct.")

    out_dir = str(Path(args.out_dir).resolve())
    destination_dir = str(Path(args.dest_dir).resolve())
    cleanup_dirs = (out_dir, REPOSITORY_ROOT / "zig" / ".zig-cache") if not args.keep_cache else (out_dir,)

    run_build(release_mode=args.release_mode, out_dir=out_dir)
    copy_and_rename_libs(out_dir, destination_dir)
    cleanup(*cleanup_dirs)
    logger.info("Done.")


if __name__ == "__main__":
    main()
