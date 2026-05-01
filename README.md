# pi4py

`pi4py` packages a Python launcher for the `@jamwil/pi` npm CLI.

`@jamwil/pi` is a slow fork of `@mariozechner/pi-coding-agent`.

The primary use for this is to expose a self-contained `pi` executable that can
be used from python using rpc mode.

## What it installs

- a `pi` console script
- `nodejs-wheel-binaries` as the bundled Node.js runtime
- a build hook that installs the pinned `@jamwil/pi` npm package and packages
  the resulting npm runtime into the Python wheel

## Usage

Install the wheel and invoke the console script with `pi` from the command line
or from Python with `subprocess.Popen`:

```python
import subprocess

process = subprocess.Popen(["pi", "--help"])
process.wait()
```

The `pi` entry point launches the bundled `@jamwil/pi` CLI with the bundled
Node.js executable. The npm dependencies, including `@jamwil/pi` itself, are
installed during wheel build / pip install from sdist, not on first launch.

It also routes `npm`, `npx`, `node`, and `corepack` lookups to bundled shims and
isolates npm global installs under `PI_CODING_AGENT_DIR/npm-global` by default.

Useful environment variables:

- `PI4PY_NPM_PREFIX`: override the npm global prefix used by launched pi
  subprocesses
- `PI4PY_SKIP_NPM_BUILD`: skip the npm build hook for metadata/debug builds
  only; the resulting package will not run unless a runtime is already present

## Updating the pinned pi version

Sync dependencies, then update the pinned npm version:

```bash
uv sync
uv run python tools/update_pi_version.py --version 0.66.1-jamwil.0
```

## Building

```bash
uv build
```

Building downloads the pinned `@jamwil/pi` npm package plus its production npm
dependencies into `src/pi4py/_vendor/npm_runtime`, prunes the runtime, and
includes it in the wheel.
