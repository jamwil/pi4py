from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from nodejs_wheel import executable as nodejs_executable

_ROOT_DIR = Path(nodejs_executable.ROOT_DIR)


def node_executable() -> str:
    if os.name == "nt":
        return str(_ROOT_DIR / "node.exe")
    return str(_ROOT_DIR / "bin" / "node")


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


if __name__ == "__main__":
    raise SystemExit(main())
