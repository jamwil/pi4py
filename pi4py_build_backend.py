from __future__ import annotations

import json
import os
import shutil
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from setuptools import build_meta as _setuptools_build_meta
from setuptools.build_meta import *  # noqa: F401,F403 - re-export PEP 517 hooks

try:
    from nodejs_wheel.executable import npm
except Exception as exc:  # pragma: no cover - build-time dependency error path
    npm = None  # type: ignore[assignment]
    _NODE_IMPORT_ERROR = exc
else:
    _NODE_IMPORT_ERROR = None

PROJECT_ROOT = Path(__file__).resolve().parent
RUNTIME_DIR = PROJECT_ROOT / "src" / "pi4py" / "_vendor" / "npm_runtime"
BUILD_LIB_RUNTIME_DIR = PROJECT_ROOT / "build" / "lib" / "pi4py" / "_vendor" / "npm_runtime"
RUNTIME_METADATA = RUNTIME_DIR / "runtime.json"
PI_PACKAGE_NAME = "@jamwil/pi-coding-agent"
PI_VERSION = "v0.84.3-dev.3"
STANDALONE_PREFIX = PurePosixPath("package/dist/standalone")


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


def _extract_standalone(package_tarball: Path) -> None:
    prefix_parts = STANDALONE_PREFIX.parts

    with tarfile.open(package_tarball, "r:gz") as archive:
        for member in archive.getmembers():
            member_path = PurePosixPath(member.name)
            if member_path.parts[: len(prefix_parts)] != prefix_parts:
                continue

            relative_path = PurePosixPath(*member_path.parts[len(prefix_parts) :])
            if not relative_path.parts:
                continue
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise RuntimeError(f"Unsafe path in npm package: {member.name}")

            destination = RUNTIME_DIR.joinpath(*relative_path.parts)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise RuntimeError(f"Unsupported entry in standalone runtime: {member.name}")

            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"Could not read standalone runtime entry: {member.name}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
            destination.chmod(member.mode)

    cli_js = RUNTIME_DIR / "cli.mjs"
    if not cli_js.is_file():
        raise RuntimeError(f"Standalone pi CLI was not found in {package_tarball}")


def _fetch_runtime(download_dir: Path, env: dict[str, str]) -> None:
    _run_npm(
        ["pack", f"{PI_PACKAGE_NAME}@{PI_VERSION}", "--ignore-scripts"],
        cwd=download_dir,
        env=env,
    )

    package_tarballs = list(download_dir.glob("*.tgz"))
    if len(package_tarballs) != 1:
        raise RuntimeError(
            f"Expected one npm package tarball, found {len(package_tarballs)} in {download_dir}"
        )
    _extract_standalone(package_tarballs[0])


def _clean_runtime() -> None:
    # Wipe both the source tree and any stale setuptools build/lib copy so
    # files removed upstream (e.g. the pre-standalone node_modules tree) don't
    # get merged back into the wheel on a rebuild.
    shutil.rmtree(RUNTIME_DIR, ignore_errors=True)
    shutil.rmtree(BUILD_LIB_RUNTIME_DIR, ignore_errors=True)
    RUNTIME_METADATA.unlink(missing_ok=True)


def _build_pi_runtime() -> None:
    if os.environ.get("PI4PY_SKIP_NPM_BUILD"):
        return

    _clean_runtime()
    env = _build_env()

    RUNTIME_DIR.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="pi4py-build-") as temp_dir_name:
        _fetch_runtime(Path(temp_dir_name), env)

    RUNTIME_METADATA.write_text(
        json.dumps(
            {
                "package": PI_PACKAGE_NAME,
                "version": PI_VERSION,
                "source": "npm-pack:dist/standalone",
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
