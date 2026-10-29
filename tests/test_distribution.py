# Copyright (c) 2026, beyondlm.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Exercise the installed discovery entry point and the bundled reset dataset."""

import hashlib
import importlib.metadata
import json

import gymnasium as gym
import numpy as np
import pytest

from allegro_inhand.assets import ASSETS_DIR, DEFAULT_GRASP_CACHE, DEFAULT_POLICY_CHECKPOINT


def test_installed_task_discovery():
    entry_points = importlib.metadata.entry_points(group="isaaclab.tasks", name="allegro_inhand")
    (entry_point,) = entry_points
    entry_point.load()
    for task_id in ("IsaacContrib-Inhand-Roll-Allegro-v0", "IsaacContrib-Inhand-Rotate-Grasp-Allegro-v0"):
        spec = gym.spec(task_id)
        assert spec.entry_point.startswith("allegro_inhand.tasks.")
        assert spec.kwargs["env_cfg_entry_point"].startswith("allegro_inhand.tasks.")
        assert spec.kwargs["rsl_rl_cfg_entry_point"].startswith("allegro_inhand.tasks.")


def test_bundled_reset_resources(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    cylinder = ASSETS_DIR / "cylinder_nv_logo.usd"
    assert cylinder.is_file()
    assert not cylinder.read_bytes().startswith(b"version https://git-lfs.github.com/spec/")
    assert (ASSETS_DIR / "nvidia-logo-vert-rgb-blk-no-reg-for-screen.png").is_file()
    cache = np.load(DEFAULT_GRASP_CACHE, allow_pickle=False)
    assert cache.shape == (50000, 23)
    assert np.isfinite(cache).all()
    np.testing.assert_allclose(np.linalg.norm(cache[:, 19:23], axis=1), 1.0, atol=1.0e-3)
    metadata = json.loads((DEFAULT_POLICY_CHECKPOINT.parent / "metadata.json").read_text())
    assert hashlib.sha256(DEFAULT_POLICY_CHECKPOINT.read_bytes()).hexdigest() == metadata["sha256"]


def test_runtime_configurations_resolve():
    """Registered configs must load against the pinned runtime, including the PPO model schema."""
    try:
        importlib.metadata.version("isaaclab")
        importlib.metadata.version("isaacsim")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("Requires the optional Isaac Lab / Isaac Sim runtime")

    from isaaclab.utils import validate

    from isaaclab_tasks.utils import load_cfg_from_registry

    import allegro_inhand.tasks  # noqa: F401

    for task_id in ("IsaacContrib-Inhand-Roll-Allegro-v0", "IsaacContrib-Inhand-Rotate-Grasp-Allegro-v0"):
        validate(load_cfg_from_registry(task_id, "env_cfg_entry_point"))
        validate(load_cfg_from_registry(task_id, "rsl_rl_cfg_entry_point"))
