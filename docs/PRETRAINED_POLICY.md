# Pretrained rolling policy

The bundled policy is copied unchanged from the original PR checkout's experiment
`logs/rsl_rl/allegro_inhand_roll/2026-08-01_20-45-00/model_1499.pt`.
It was selected from five complete original checkpoints evaluated in the new external project.

- File: `src/allegro_inhand/assets/data/checkpoints/allegro_inhand_roll.pt`.
- SHA-256: `f80bc191be2ec6725724e85bb904e5ec57113c304c27bee5832b523b8d9b3809`.
- Network: normalized 121-dimensional observations; ELU MLP layers 512, 256, 128; 16 actions.
- Serialization: actor and critic state dictionaries; directly compatible with the pinned RSL-RL 5.5 runtime.
- Training base commit: `0f577c72e86f3df3e2a7f7960e02729b413d9d42`, with a dirty working tree recorded in the original run.
- Saved training-diff SHA-256: `77e36a26051ca0706ae40437765dc7703cf3c6e2108238eaf809cd943b8a5a15`.
- Machine-readable provenance: `assets/data/checkpoints/metadata.json` inside the installed package.

The recorded training base and saved diff identify the original run's source state; an exact clean training commit
is not available. The historical GIF has not been matched to this checkpoint.

## Comparison of original checkpoints

Every candidate used 64 environments, seed 42, 1,200 policy steps (40 seconds per environment), gravity
`[0, 0, -10]`, and a disabled gravity curriculum. Each run completed 128 episodes and produced finite observations
and rewards. Turns integrate the task's mean signed axis angular velocity across the fixed horizon, including resets.

| Original experiment | Mean turns per environment | Mean displacement (mm) | Observed drop events | Mean step reward |
| --- | ---: | ---: | ---: | ---: |
| 2026-08-01_16-14-45 | 0.774 | 0.291 | 0 | 2.266 |
| 2026-08-01_17-53-13 | 4.810 | 0.567 | 0 | 3.005 |
| 2026-08-01_19-42-57 | 9.225 | 2.216 | 0 | 2.172 |
| 2026-08-01_20-15-21 | 1.645 | 3.292 | 0 | 1.656 |
| 2026-08-01_20-45-00 | 4.600 | 0.397 | 0 | 3.278 |

The selected checkpoint had the highest mean reward in this comparison, with sub-millimeter mean displacement and
no observed drops. The faster `19-42-57` policy had larger object displacement. The selection emphasizes stable rolling.

## Independent-seed check

The packaged checkpoint was then evaluated with seed 7 using the public command:

```bash
uv run --locked --extra isaacsim allegro-evaluate --num_envs 64 --steps 1200 --seed 7 --viz none --output outputs/evaluation.json
```

Result: 4.595 mean turns per environment, 0.437 mm mean displacement, finite observations and rewards, and one drop
among 128 completed episodes. The measured object mass remained 0.16382052 kg after removing the ineffective legacy
mass declaration. These finite-sample results do not establish a zero-drop guarantee.

`metrics_time_mean["rotate/success_rate"]` averages the task's instantaneous success flag over time; interpret it
separately from episode-level success. `drop_events_estimate` sums the task's instantaneous per-step drop indicator
across the full batch and horizon. Checkpoint identity and evaluation conditions are included in each JSON report.

The real-time OpenGL policy-preview path was also checked for 60 steps under an isolated Xvfb display.
A later 60-step real desktop run also passed using the user-selected local Lab 3.0 source workflow. The author
then confirmed a 1,800-step host preview passed with three completed episodes, 6.985 integrated turns, no drops,
and finite observations and rewards. See [local source validation](LOCAL_LAB.md).
