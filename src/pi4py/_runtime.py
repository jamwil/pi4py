from __future__ import annotations

from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_RUNTIME_DIR = _PACKAGE_DIR / "_vendor" / "npm_runtime"


def install_root() -> Path:
    return _RUNTIME_DIR


def cli_path() -> Path:
    return install_root() / "node_modules" / "@jamwil" / "pi-coding-agent" / "dist" / "cli.js"


def ensure_cli() -> Path:
    pi_cli = cli_path()
    if not pi_cli.is_file():
        raise RuntimeError(
            "The bundled pi runtime is missing. Reinstall pi4py from a wheel or rebuild it "
            "without PI4PY_SKIP_NPM_BUILD."
        )
    return pi_cli
