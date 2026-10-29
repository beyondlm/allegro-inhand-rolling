# Copyright (c) 2026, beyondlm.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Project resources available from both editable installs and wheels."""

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "data"
GRASP_CACHE_PREFIX = ASSETS_DIR / "cache" / "allegro_grasp_linspace"
DEFAULT_GRASP_CACHE = ASSETS_DIR / "cache" / "allegro_grasp_linspace_0.8-0.8-1.npy"
