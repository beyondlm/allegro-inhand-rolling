# Source and ownership

This standalone project was extracted from [Isaac Lab PR #6345](https://github.com/isaac-sim/IsaacLab/pull/6345).
Its independent repository is [beyondlm/allegro-inhand-rolling](https://github.com/beyondlm/allegro-inhand-rolling);
it is not a fork of Isaac Lab.

- Task source: `beyondlm/IsaacLab`, branch `feature/allegro-rotate-cylinder`.
- Extraction commit: `8bf8bae5d7fa62752c7809ac0cb7463c7a9dc42f`.
- Official upstream dependency: `isaac-sim/IsaacLab` at `46d6cc3d7b115906fad12efd372fbf69f4e3d3ed`.
- Project maintainer: beyondlm; project support and compatibility updates belong in
  [this repository's issue tracker](https://github.com/beyondlm/allegro-inhand-rolling/issues).
- Task IDs, reward equations, observation layout, control settings, and cached reset states are retained from that source.

The external project owns task registration, package resource paths, command entry points, and writable output paths.
Compatibility adaptations use scene-owned asset cloning, canonical actuator-limit fields, and the RSL-RL 5.5 actor/critic
model schema. Network sizes, normalization, initial action standard deviation, and PPO hyperparameters are retained.
It does not require copying files into an Isaac Lab checkout.

## Assets

- Hand: the official `isaaclab_assets.robots.allegro.ALLEGRO_HAND_CFG`; downloaded by Isaac Lab on first use.
  The original SimLab license is reproduced in [licenses/allegro-hand-license.txt](licenses/allegro-hand-license.txt).
- Cylinder and adjacent logo texture: copied without modification from the task's tracked assets.
  The NVIDIA logo is a third-party mark; project licensing does not grant trademark rights.
- Grasp cache: the original 50,000-row reset dataset for cylinder scale 0.8. Rows contain 16 joint positions,
  object XYZ, then object quaternion XYZW. Regenerate it when changing assets, joint conventions, or cylinder scales.
- Policy: the original `2026-08-01_20-45-00/model_1499.pt`, retained without conversion. See
  [policy provenance and results](PRETRAINED_POLICY.md) for its recorded training state and external-project validation.
- Demo: the original task GIF; it is historical evidence, not a new validation of the external package.

The source's BSD-3-Clause notices and repository LICENSE are preserved. Confirm the cylinder/texture provenance and
redistribution terms before the first public release.

## Resource checksums

| Resource | SHA-256 |
| --- | --- |
| `cylinder_nv_logo.usd` | `df9842072c92e8170ede57139626463c869b42638a2a8a780f3ed9b728d85581` |
| `nvidia-logo-vert-rgb-blk-no-reg-for-screen.png` | `f514796ed3fdbca5513275c5a97158ef6c6359f6b8d2d3a0fe0645a632608179` |
| `allegro_grasp_linspace_0.8-0.8-1.npy` | `e5431335584da7ece062e8565c8c00f5312041db64b864fdaf32506156468b64` |
| `allegro_rotate_demo.gif` | `cfe2278181e6fc8050aa77707a1ea4c755588f9f8128b1d7bee1c28ac6676549` |
| `allegro_inhand_roll.pt` | `f80bc191be2ec6725724e85bb904e5ec57113c304c27bee5832b523b8d9b3809` |
