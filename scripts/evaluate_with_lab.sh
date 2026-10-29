#!/usr/bin/env bash
# Copyright (c) 2026, beyondlm.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

if (( $# < 2 )); then
    printf 'Usage: %s <isaaclab-source-root> <python-environment-root> [evaluation arguments...]\n' "$0" >&2
    exit 2
fi

allegro_lab_root=$(realpath -- "$1")
allegro_env_root=$(realpath -- "$2")
allegro_project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
shift 2

if [[ ! -f "$allegro_lab_root/pyproject.toml" || ! -x "$allegro_env_root/bin/python" ]]; then
    printf 'Expected an Isaac Lab source checkout and a Python environment containing bin/python.\n' >&2
    exit 2
fi

# Keep the selected interpreter's stdlib and installed packages ahead of the
# additional Python paths supplied by a linked Isaac Sim build.
allegro_python_paths=$(env -u PYTHONHOME -u PYTHONPATH -u LD_LIBRARY_PATH -u LD_PRELOAD \
    "$allegro_env_root/bin/python" -I -c 'import os,sysconfig; s=sysconfig.get_path("stdlib"); print(os.pathsep.join([s,os.path.join(s,"lib-dynload"),sysconfig.get_path("purelib")]))')

# Let the chosen Lab launcher establish its own native-library paths. Do not
# inherit paths from another Isaac Sim installation in the calling terminal.
allegro_clean_env=(env -u LD_LIBRARY_PATH -u LD_PRELOAD -u PYTHONPATH -u PYTHONHOME
    "VIRTUAL_ENV=$allegro_env_root" "PYTHONPATH=$allegro_project_root/src:$allegro_python_paths" "PYTHONNOUSERSITE=1")

"${allegro_clean_env[@]}" uv run --project "$allegro_lab_root" --active --no-sync python -u - "$allegro_lab_root" <<'PY'
import subprocess
import sys
from pathlib import Path

import isaaclab
from isaaclab.paths import ISAACLAB_ROOT

expected_root = Path(sys.argv[1]).resolve()
actual_root = Path(ISAACLAB_ROOT).resolve()
if actual_root != expected_root:
    raise SystemExit(f"Wrong Isaac Lab checkout: imported {actual_root}, expected {expected_root}")
revision = subprocess.check_output(["git", "-C", str(actual_root), "rev-parse", "--short", "HEAD"], text=True).strip()
print(f"Python: {sys.executable}", flush=True)
print(f"Isaac Lab: {actual_root} ({(actual_root / 'VERSION').read_text().strip()}, {revision})", flush=True)
print(f"Framework module: {isaaclab.__file__}", flush=True)
print(f"Linked Isaac Sim: {(actual_root / '_isaac_sim').resolve()}", flush=True)
PY

exec "${allegro_clean_env[@]}" uv run --project "$allegro_lab_root" --active --no-sync \
    isaaclab -p -X faulthandler -u -m allegro_inhand.tools.allegro_evaluate "$@"
