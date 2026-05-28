from __future__ import annotations

import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME_ROOT = PROJECT_ROOT / "src" / "pi4py" / "_vendor" / "npm_runtime" / "node_modules"

REMOVABLE_DIRECTORIES = {
    ".github",
    ".husky",
    "__mocks__",
    "__tests__",
    "benchmark",
    "benchmarks",
    "coverage",
    "docs",
    "example",
    "examples",
    "scripts",
    "test",
    "tests",
}

REMOVABLE_SUFFIXES = (
    ".d.cts.map",
    ".d.mts.map",
    ".d.ts.map",
    ".js.map",
    ".mjs.map",
    ".cjs.map",
    ".cts",
    ".mts",
    ".ts",
    ".tsx",
    ".map",
)

REMOVABLE_NAMES = {
    ".babelrc",
    ".editorconfig",
    ".eslintignore",
    ".eslintrc",
    ".eslintrc.cjs",
    ".eslintrc.js",
    ".gitattributes",
    ".gitignore",
    ".npmignore",
    ".nycrc",
    ".prettierignore",
    ".prettierrc",
    ".prettierrc.json",
    ".prettierrc.yaml",
    ".travis.yml",
    "appveyor.yml",
    "bower.json",
    "changelog",
    "changelog.md",
    "changelog.markdown",
    "contributing.md",
    "eslint.config.js",
    "gruntfile.js",
    "gulpfile.js",
    "makefile",
    "package-lock.json",
    "pnpm-lock.yaml",
    "readme",
    "readme.md",
    "readme.markdown",
    "rollup.config.js",
    "tsconfig.json",
    "tsconfig.build.json",
    "typedoc.json",
    "yarn.lock",
}

# Keep pi's own user-facing docs/examples because the system prompt points to them.
KEEP_PREFIX_PARTS = {
    ("@jamwil", "pi", "docs"),
    ("@jamwil", "pi", "examples"),
}


def _relative_parts(path: Path, root: Path) -> tuple[str, ...]:
    try:
        return path.relative_to(root).parts
    except ValueError:
        return ()


def _is_kept(path: Path, root: Path) -> bool:
    parts = _relative_parts(path, root)
    if any(parts[: len(prefix)] == prefix for prefix in KEEP_PREFIX_PARTS):
        return True
    return parts[:2] == ("@jamwil", "pi") and path.name.lower() in {"readme.md", "changelog.md"}


def prune_npm_runtime(root: Path = DEFAULT_RUNTIME_ROOT) -> None:
    if not root.is_dir():
        return

    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if _is_kept(path, root):
            continue

        lower_name = path.name.lower()
        if path.is_dir():
            if lower_name in REMOVABLE_DIRECTORIES:
                shutil.rmtree(path, ignore_errors=True)
            continue

        if not path.is_file():
            continue

        if lower_name in REMOVABLE_NAMES or lower_name.endswith(REMOVABLE_SUFFIXES):
            path.unlink()


def main() -> int:
    prune_npm_runtime()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
