import subprocess
import os
import logging

from argparse import ArgumentParser, Namespace
from shutil import copy2, rmtree

logger = logging.getLogger(__name__)


def check_zig_version() -> str:
    try:
        result = subprocess.run(["zig", "version"], capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError("Zig is not installed or not found in PATH.")

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(
            f"'zig version' failed (return code: {result.returncode}). "
            f"Stderr: {stderr}."
        )

    version = (result.stdout or "").strip()
    logger.info("Found Zig version: %s", version)
    return version


def run_build(release_mode: bool) -> None:
    args = ["zig", "build", "--summary", "all"]
    if release_mode:
        args.append("--release=fast")

    logger.info("Running: %s", " ".join(args))
    result = subprocess.run(args, cwd="zig")
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
    p.add_argument("--out-dir", default="zig/zig-out", help="Build output directory.")
    p.add_argument(
        "--dest-dir",
        default="zyra/bindings/native",
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
    assert check_zig_version() == "0.14.1", "Invalid zig version."
    logger.info("The zig version is correct.")

    out_dir = args.out_dir
    destination_dir = args.dest_dir
    cleanup_dirs = (out_dir, "zig/.zig-cache") if not args.keep_cache else (out_dir,)

    run_build(release_mode=args.release_mode)
    copy_and_rename_libs(out_dir, destination_dir)
    cleanup(*cleanup_dirs)
    logger.info("Done.")


if __name__ == "__main__":
    main()
