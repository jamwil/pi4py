from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from nodejs_wheel import executable as nodejs_executable

_ROOT_DIR = Path(nodejs_executable.ROOT_DIR)


def get_node_binary() -> str:
    """Return the path to the Node.js binary bundled by ``nodejs-wheel``.

    ``nodejs-wheel`` installs the binary alongside its Python package in the
    active environment, so this resolves to the binary in the venv running the
    current Python interpreter rather than relying on ``PATH``.
    """
    binary_name = "node.exe" if os.name == "nt" else "bin/node"
    binary = _ROOT_DIR / binary_name
    if not binary.is_file():
        raise FileNotFoundError(
            f"The nodejs-wheel Node.js binary was not found at {binary}"
        )
    return str(binary)


def node_executable() -> str:
    """Backward-compatible alias for :func:`get_node_binary`."""
    return get_node_binary()


def npm_cli() -> str:
    return str(_ROOT_DIR / "lib" / "node_modules" / "npm" / "bin" / "npm-cli.js")


def npx_cli() -> str:
    return str(_ROOT_DIR / "lib" / "node_modules" / "npm" / "bin" / "npx-cli.js")


def corepack_cli() -> str:
    return str(_ROOT_DIR / "lib" / "node_modules" / "corepack" / "dist" / "corepack.js")


def command_argv(command: str, args: list[str]) -> list[str]:
    if command == "node":
        return [node_executable(), *args]
    if command == "npm":
        return [node_executable(), npm_cli(), *args]
    if command == "npx":
        return [node_executable(), npx_cli(), *args]
    if command == "corepack":
        return [node_executable(), corepack_cli(), *args]
    raise ValueError(f"Unsupported nodejs helper command: {command}")


def run(command: str, args: list[str]) -> int:
    argv = command_argv(command, args)
    if os.name != "nt":
        os.execv(argv[0], argv)
    return subprocess.call(argv, close_fds=False)


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m pi4py._nodejs <node|npm|npx|corepack> [args...]")
    return run(sys.argv[1], sys.argv[2:])


def node_path_main() -> int:
    """Print the path to the bundled Node.js binary."""
    print(get_node_binary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
