# Validation

Checked on 2026-10-29 on Linux x86-64, an RTX 5880 Ada, and NVIDIA driver 580.178.04.
Checks cover packaging, runtime integration, and fixed-horizon evaluation of the original pretrained policy.
Full training from scratch has not been reproduced.

## Revisions and environment

- Task source: PR commit `8bf8bae5d7fa62752c7809ac0cb7463c7a9dc42f`.
- Dependency: official Isaac Lab commit `46d6cc3d7b115906fad12efd372fbf69f4e3d3ed`.
- `uv.lock`: 283 packages; aggregate Isaac Lab 3.0.0, Isaac Sim 6.2.0.0, PyTorch 2.11.0+cu130, RSL-RL 5.5.1.
- The independent environment was installed with `uv sync --extra isaacsim --locked`. Import paths point to this
  project's `.venv`; `isaaclab_tasks.contrib.allegro_rotate` is absent.
- Upstream dependency overrides are retained because the wheel does not propagate workspace overrides and Isaac
  Sim's Newton and urllib3 declarations conflict with the pinned Isaac Lab revision's requirements.
- Optional predownloaded extension caches are a separate `extscache` extra. The original PR environment contains
  Isaac Sim 6.0.0.1; it was not reused as validation for this independent 6.2 environment.
- The author accepted the NVIDIA Omniverse EULA during the first host launch.

## Passed checks

| Check | Result |
| --- | --- |
| Locked installation, Ruff lint/format, wheel and source archive build | Passed |
| Installed wheel tests from `/tmp`, without Isaac Lab | 2 passed; runtime configuration test skips without the runtime |
| Full environment configuration and distribution tests | 3 passed; upstream deprecation warnings remain |
| Supplied cache score | PASS, 97.5228; 50,000 by 23 float32 values, no NaN or Inf |
| PhysX cache viewer, `--num_envs 4 --steps 100 --viz none` | Passed; source cache loaded and environment stepped |
| Grasp generator, 16 environments, 16 target rows, 2,000-step cap | Passed; 16 rows saved under `outputs/validation/` |
| PPO, 32 environments, 3 iterations, no visualizer | Passed; `model_0.pt` and `model_2.pt` saved |
| Checkpoint playback, 4 environments, 50 steps, gravity -10 m/s², curriculum disabled | Passed; finite observations and rewards; JIT and ONNX export completed |
| `newton_gl`, 20 steps with no display (EGL) | Passed; no window requested |
| `newton_gl`, 60 steps under an isolated Xvfb display | Passed; visible-viewer code path exercised |
| Five original 1,499-iteration policies, 64 environments and 1,200 steps each | Direct loading passed; results in PRETRAINED_POLICY.md |
| Packaged original policy, independent seed 7, same evaluation horizon | Passed; 4.595 turns per environment, one observed drop among 128 episodes |
| Real-time packaged-policy preview, 60 steps under Xvfb | Passed; JSON written before Kit shutdown |

Playback uses the official RSL-RL backend with a temporary harness limiting only the playback loop to 50 inference-mode
steps. That temporary loop bound is not part of the package. This initial smoke-test checkpoint has only three
training iterations. The separately packaged original 1,499-iteration policy is evaluated in PRETRAINED_POLICY.md.

Logs and generated artifacts are under the git-ignored `outputs/validation/` and `logs/rsl_rl/allegro_inhand_roll/`.
The lightweight wheel environment uses Python 3.12.13, NumPy 2.5.4, Gymnasium 1.4.0, and pytest 9.2.0.
The GitHub Actions workflow reproduces lightweight packaging checks; it has not yet run on GitHub.

## Compatibility adaptations

The extracted task had stale APIs after merging its newer upstream base. Runtime checks exposed and resolved:

- Removed `ClonePlan.from_env_0`: final asset configurations are now attached before the base environment builds
  the scene, letting the scene own construction, cloning, and contact-sensor replication.
- Removed `RslRlPpoActorCriticCfg`: use separate actor and critic MLP configurations with the original network sizes,
  normalization, initial standard deviation, and PPO hyperparameters.
- Conflicting deprecated grasp actuator limits: use `joint_effort_limit` and `actuator_effort_limit`, both 2.0.

Reward equations, observation construction, action processing, and reset logic are unchanged. The public evaluator
loads the packaged policy directly, uses inference mode, fixes gravity with no curriculum, and emits JSON before Kit
closes. RL runtime imports are deferred until Kit initialization to avoid premature plugin initialization.

## Graphics limitation

The host `--viz kit` launch exited 139 in `libnvidia-rtcore.so.580.178.04` / the Vulkan graphics plugin while
`SimulationApp._wait_for_viewport` was running, before constructing the task environment. The exact driver-level root
cause is not established. Headless PhysX and the Newton OpenGL viewer avoid that failing RTX path.

Isaac Sim 6.2's [requirements page](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/requirements.html)
lists Linux driver 595.58.03 as its tested driver. The general
[Omniverse requirements](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html)
also list R580 for Ada GPUs, so the crash alone does not establish that every R580 version is unsupported.
No host drivers or system graphics configuration were changed. The source-based launcher has subsequently passed
on the actual host X display using the selected local Lab 3.0 checkout and native Sim build; see
[local source validation](LOCAL_LAB.md). The standalone pip-environment host failure and the Kit/RTX failure are not
claimed to be fixed by that separate source-based result.

## Remaining baseline and release work

- The inherited cylinder USD lacks a mass schema, so the legacy 0.05 kg declaration was a no-op. That misleading
  declaration has been removed. The density-derived mass remains 0.16382052 kg, as verified before and after the
  change; the packaged original policy was evaluated with this mass. Applying 0.05 kg would change task physics.
- Other upstream schema-deprecation and USD diagnostic warnings remain. Newton physics is not part of the tested
  compatibility claim; the OpenGL viewer tests still use PhysX physics.
- The original checkpoint has been packaged and evaluated without conversion; its exact match to the historical
  GIF remains unverified. Earlier direct host logs were empty; the new source-based launch has completed on the
  real desktop display with a finite-value JSON result.
- Confirm cylinder/texture provenance and redistribution terms with the author.
- Publish a versioned repository/release, then link it in PR #6345 for maintainer review and README listing.

## Selected local Lab 3.0 source

The user-selected source checkout `e3f7d9ff1f` and its existing named Python environment were verified through
`scripts/evaluate_with_lab.sh`, including 100 headless steps, 60 real desktop OpenGL steps, and a 64-environment,
1,200-step seed-7 evaluation. The author then confirmed a 1,800-step host OpenGL run passed: three completed
episodes, 6.985 integrated turns, no drops, and finite observations and rewards. The helper does not install into
or synchronize that environment. Details and precise results are recorded in [LOCAL_LAB.md](LOCAL_LAB.md).
