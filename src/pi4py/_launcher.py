from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pi4py._nodejs import node_executable
from pi4py._runtime import ensure_cli

_PACKAGE_DIR = Path(__file__).resolve().parent
_SHIM_DIR = _PACKAGE_DIR / "_shim"


def _build_env() -> dict[str, str]:
    env = os.environ.copy()
    path = env.get("PATH")
    shim_dir = str(_SHIM_DIR)
    env["PATH"] = shim_dir if not path else os.pathsep.join([shim_dir, path])
    env["PI4PY_PYTHON_EXECUTABLE"] = sys.executable

    agent_dir = Path(env.get("PI_CODING_AGENT_DIR", Path.home() / ".pi" / "agent"))
    npm_prefix = Path(env.get("PI4PY_NPM_PREFIX", agent_dir / "npm-global"))
    npm_prefix.mkdir(parents=True, exist_ok=True)
    env.setdefault("NPM_CONFIG_PREFIX", str(npm_prefix))
    env.setdefault("npm_config_prefix", str(npm_prefix))

    env.setdefault("npm_config_update_notifier", "false")
    env.setdefault("npm_config_fund", "false")
    return env


def _argv(env: dict[str, str]) -> list[str]:
    try:
        pi_cli = ensure_cli()
    except Exception as exc:
        raise SystemExit(f"Unable to locate bundled @jamwil/pi runtime: {exc}") from exc

    return [node_executable(), str(pi_cli), *sys.argv[1:]]


def main() -> int:
    env = _build_env()
    argv = _argv(env)

    if os.name != "nt":
        os.execvpe(argv[0], argv, env)

    return subprocess.call(argv, env=env, close_fds=False)


if __name__ == "__main__":
    raise SystemExit(main())
