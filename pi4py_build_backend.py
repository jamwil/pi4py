from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from setuptools import build_meta as _setuptools_build_meta
from setuptools.build_meta import *  # noqa: F401,F403 - re-export PEP 517 hooks

from tools.prune_npm_runtime import prune_npm_runtime

try:
    from nodejs_wheel.executable import npm
except Exception as exc:  # pragma: no cover - build-time dependency error path
    npm = None  # type: ignore[assignment]
    _NODE_IMPORT_ERROR = exc
else:
    _NODE_IMPORT_ERROR = None

PROJECT_ROOT = Path(__file__).resolve().parent
RUNTIME_DIR = PROJECT_ROOT / "src" / "pi4py" / "_vendor" / "npm_runtime"
RUNTIME_METADATA = PROJECT_ROOT / "src" / "pi4py" / "_vendor" / "runtime.json"
PI_PACKAGE_NAME = "@jamwil/pi-coding-agent"
PI_VERSION = "0.76.1-jamwil.0"


def _run_npm(args: list[str], cwd: Path, env: dict[str, str]) -> None:
    if npm is None:
        raise RuntimeError(
            "nodejs-wheel-binaries is required to build the pi runtime"
        ) from _NODE_IMPORT_ERROR
    npm(args, cwd=str(cwd), env=env, check=True)


def _build_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("npm_config_audit", "false")
    env.setdefault("npm_config_fund", "false")
    env.setdefault("npm_config_update_notifier", "false")
    env.setdefault("npm_config_progress", "false")
    env.setdefault("npm_config_loglevel", "warn")
    return env


def _install_runtime(runtime_project_dir: Path, env: dict[str, str]) -> None:
    (runtime_project_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "pi4py-runtime",
                "private": True,
                "dependencies": {PI_PACKAGE_NAME: PI_VERSION},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    _run_npm(
        [
            "install",
            "--omit=dev",
            "--omit=optional",
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
        ],
        cwd=runtime_project_dir,
        env=env,
    )

    cli_js = runtime_project_dir / "node_modules" / "@jamwil" / "pi-coding-agent" / "dist" / "cli.js"
    if not cli_js.is_file():
        raise RuntimeError(f"Installed pi CLI was not found: {cli_js}")

    shutil.rmtree(runtime_project_dir / "node_modules" / ".bin", ignore_errors=True)


def _clean_runtime() -> None:
    shutil.rmtree(RUNTIME_DIR, ignore_errors=True)
    RUNTIME_METADATA.unlink(missing_ok=True)


def _build_pi_runtime() -> None:
    if os.environ.get("PI4PY_SKIP_NPM_BUILD"):
        return

    _clean_runtime()
    env = _build_env()

    with tempfile.TemporaryDirectory(prefix="pi4py-build-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        runtime_project_dir = temp_dir / "runtime"
        runtime_project_dir.mkdir()

        _install_runtime(runtime_project_dir, env)

        RUNTIME_DIR.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(runtime_project_dir / "node_modules", RUNTIME_DIR / "node_modules")
        prune_npm_runtime(RUNTIME_DIR / "node_modules")
        shutil.copy2(runtime_project_dir / "package.json", RUNTIME_DIR / "package.json")
        package_lock = runtime_project_dir / "package-lock.json"
        if package_lock.is_file():
            shutil.copy2(package_lock, RUNTIME_DIR / "package-lock.json")

    RUNTIME_METADATA.write_text(
        json.dumps(
            {
                "package": PI_PACKAGE_NAME,
                "version": PI_VERSION,
                "source": "npm",
                "built_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    _build_pi_runtime()
    return _setuptools_build_meta.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    _build_pi_runtime()
    return _setuptools_build_meta.build_editable(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory, config_settings=None):
    # Keep sdists source-only. Wheels built from the sdist will run build_wheel
    # and generate src/pi4py/_vendor/npm_runtime then.
    _clean_runtime()
    return _setuptools_build_meta.build_sdist(sdist_directory, config_settings)
