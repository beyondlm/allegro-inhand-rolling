# Validation with an existing Lab 3.0 source checkout

The source-based workflow was verified on 2026-10-29 with:

- Lab checkout: `projects/IsaacLab_3.0`, application `VERSION` 3.0.0.
- Source commit: `e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4`.
- Python environment: that checkout's `isaaclab_3.0`, Python 3.12.13.
- Sim runtime: its `_isaac_sim` link to the existing `IsaacSim-6.2/_build/linux-x86_64/release` build.
- RSL-RL 5.5.1, PyTorch 2.11.0+cu130, and matching PyOpenGL / PyOpenGL-accelerate 4.0.0a8 packages.
- The leaf Isaac Lab distribution reports 28.0.0; application release identification comes from the checkout's
  `VERSION` file and commit, rather than assuming every source package shares that version.

The checkout also contains an older `.venv` with Python 3.10 and Isaac Sim 4.5. The verified source workflow uses
its named `isaaclab_3.0` environment. No tracked source files or installed package versions in that checkout were changed.

## Launch

From this external project's root, supply the selected source checkout and environment root:

```bash
scripts/evaluate_with_lab.sh /path/to/IsaacLab_3.0 /path/to/IsaacLab_3.0/isaaclab_3.0 --num_envs 1 --steps 1800 --viz newton_gl --real-time --output outputs/validation/local-desktop.json
```

The script prints the Python interpreter, imported Lab source root, release/commit, and linked Sim location before
launching. It imports this external task through its own `src` path, so installation into the selected environment
is unnecessary. It preserves the caller's display settings and does not synchronize the selected environment.

The native Sim launcher adds its own Python search paths. During investigation, a crash was captured while Warp
imported `inspect` from Kit's standard library rather than the selected interpreter's standard library. The source
launcher now prioritizes the selected interpreter's stdlib, dynamic extensions, and site-packages before the additional
Kit paths. It also clears inherited `PYTHONHOME`, `PYTHONPATH`, `LD_LIBRARY_PATH`, and `LD_PRELOAD` for this process;
`isaaclab -p` then establishes the selected native runtime's paths.

This earlier Lab source retains deprecated stochastic-model fields. The evaluator invokes its public
`handle_deprecated_rsl_rl_cfg` helper when those fields are present, following the selected checkout's official RL
entrypoints. Current source layouts without those fields use the existing direct configuration path.

## Results

| Check | Result |
| --- | --- |
| Source/interpreter/linked-runtime path verification | Passed |
| 4 environments, 100 policy steps, fixed -10 m/s² gravity, no visualizer | Passed; finite observations and rewards |
| Real host X display `:1`, OpenGL, real time, 60 policy steps | Passed; exit 0, JSON report generated |
| Author-run host OpenGL preview, real time, 1,800 policy steps | Passed; author confirmed the visual test, finite JSON result, no drops |
| 64 environments, seed 7, 1,200 steps (40 simulated seconds per environment) | Passed; results below |

The full evaluation completed 128 episodes. Mean integrated rotation was 4.59493 turns per environment, mean object
displacement was 0.43677 mm, and one drop event was observed. The measured mass was 0.16382052 kg. These results
match the prior locked-environment seed-7 evaluation. They are finite-sample evidence rather than a no-drop guarantee.

The author subsequently ran the source launcher on the host for 1,800 steps with one environment and seed 42,
then confirmed the visual test passed. The run completed three episodes over 60 simulated seconds, integrated
6.98494 turns, and recorded no drop events. Mean object displacement was 0.37103 mm, and all observations and
rewards were finite. The raw report is `outputs/validation/host-lab3.json`; a path-independent copy is retained in
the packaged checkpoint metadata under `host_desktop_validation`.

The actual desktop runs use the existing Xorg display, unlike the earlier Xvfb checks. The Kit/RTX viewer is not
covered by this success; this launch uses the OpenGL viewer with PhysX physics.

Logs and JSON reports are under the git-ignored `outputs/validation/local-lab3-*` and
`outputs/validation/host-lab3.*` paths.
