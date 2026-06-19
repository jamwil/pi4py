from __future__ import annotations

import argparse
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PI_MODULE_PATH = PROJECT_ROOT / "src" / "pi4py" / "_pi.py"
BUILD_BACKEND_PATH = PROJECT_ROOT / "pi4py_build_backend.py"


def _replace_one(path: Path, pattern: str, replacement: str) -> None:
    original = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, original, count=1)
    if count != 1:
        raise RuntimeError(f"Could not update {pattern!r} in {path}")
    path.write_text(updated, encoding="utf-8")


def update_pi_version(version: str) -> None:
    _replace_one(PI_MODULE_PATH, r'PI_VERSION = "[^"]+"', f'PI_VERSION = "{version}"')
    _replace_one(BUILD_BACKEND_PATH, r'PI_VERSION = "[^"]+"', f'PI_VERSION = "{version}"')


def main() -> int:
    parser = argparse.ArgumentParser(description="Update the pinned @jamwil/pi-coding-agent version")
    parser.add_argument("--version", required=True, help="@jamwil/pi-coding-agent version to install at runtime")
    args = parser.parse_args()
    update_pi_version(args.version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
