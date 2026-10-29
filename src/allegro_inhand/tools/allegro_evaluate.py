# Copyright (c) 2026, beyondlm.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Evaluate a rolling policy for a fixed horizon at a fixed gravity."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import sys
import time
from pathlib import Path

import gymnasium as gym
import torch
import warp as wp

from isaaclab.app import add_launcher_args, launch_simulation
from isaaclab.utils import to_dict

from isaaclab_tasks.utils import resolve_task_config

import allegro_inhand.tasks  # noqa: F401
from allegro_inhand.assets import DEFAULT_POLICY_CHECKPOINT

TASK_ID = "IsaacContrib-Inhand-Roll-Allegro-v0"
METRICS = (
    "rotate/ang_vel",
    "rotate/object_pos_diff",
    "rotate/drop_rate",
    "rotate/success_rate",
    "rotate/total_reward",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkpoint", type=Path, default=DEFAULT_POLICY_CHECKPOINT, help="RSL-RL checkpoint to evaluate."
    )
    parser.add_argument("--num_envs", type=int, default=64)
    parser.add_argument("--steps", type=int, default=1200, help="Fixed number of policy steps per environment.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--real-time", action="store_true", help="Pace playback at the policy control rate.")
    parser.add_argument("--gravity", type=float, default=-10.0, help="Fixed world Z gravity in m/s².")
    parser.add_argument("--output", type=Path, help="Also write the JSON report to this file.")
    add_launcher_args(parser)
    args, hydra_args = parser.parse_known_args()
    if args.num_envs < 1 or args.steps < 1:
        parser.error("--num_envs and --steps must be positive")
    checkpoint = args.checkpoint.expanduser().resolve()
    if not checkpoint.is_file():
        parser.error(f"Checkpoint does not exist: {checkpoint}")
    sys.argv = [sys.argv[0]] + hydra_args

    env_cfg, agent_cfg = resolve_task_config(TASK_ID, "rsl_rl_cfg_entry_point")
    env_cfg.scene.num_envs = args.num_envs
    env_cfg.seed = args.seed
    env_cfg.gravity_curriculum = False
    env_cfg.sim.gravity = (0.0, 0.0, args.gravity)
    if args.device is not None:
        env_cfg.sim.device = args.device
    agent_cfg.device = env_cfg.sim.device

    with launch_simulation(env_cfg, args):
        from rsl_rl.runners import OnPolicyRunner

        from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

        # Earlier Lab 3.0 source checkouts retain fields removed by RSL-RL 5.
        # Use that checkout's own migration helper, as its official entrypoints do.
        if hasattr(agent_cfg.actor, "stochastic"):
            from isaaclab_rl.rsl_rl import handle_deprecated_rsl_rl_cfg

            agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, importlib.metadata.version("rsl-rl-lib"))

        raw_env = gym.make(TASK_ID, cfg=env_cfg)
        try:
            env = RslRlVecEnvWrapper(raw_env, clip_actions=agent_cfg.clip_actions)
            runner = OnPolicyRunner(env, to_dict(agent_cfg), log_dir=None, device=agent_cfg.device)
            runner.load(str(checkpoint), load_cfg={"actor": True, "critic": True, "iteration": True}, strict=True)
            policy = runner.get_inference_policy(device=env.unwrapped.device)
            env.unwrapped.seed(args.seed)
            sums = {key: torch.zeros((), device=env.unwrapped.device) for key in METRICS}
            all_finite = torch.ones((), dtype=torch.bool, device=env.unwrapped.device)
            episodes = torch.zeros((), device=env.unwrapped.device)
            with torch.inference_mode():
                obs, _ = env.reset()
                for _ in range(args.steps):
                    start_time = time.perf_counter()
                    obs, reward, dones, info = env.step(policy(obs))
                    policy.reset(dones)
                    all_finite &= torch.isfinite(reward).all()
                    for tensor in obs.values():
                        all_finite &= torch.isfinite(tensor).all()
                    episodes += dones.sum()
                    for key in sums:
                        sums[key] += info["log"][key]
                    if args.real_time:
                        time.sleep(max(0.0, env.unwrapped.step_dt - (time.perf_counter() - start_time)))

            means = {key: float((value / args.steps).item()) for key, value in sums.items()}
            report = {
                "task": TASK_ID,
                "checkpoint": str(checkpoint),
                "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                "checkpoint_iteration": runner.current_learning_iteration,
                "num_envs": args.num_envs,
                "steps": args.steps,
                "seed": args.seed,
                "gravity": list(env_cfg.sim.gravity),
                "gravity_curriculum": False,
                "all_finite": bool(all_finite.item()),
                "completed_episodes": int(episodes.item()),
                "metrics_time_mean": means,
                "integrated_turns_per_env": means["rotate/ang_vel"]
                * args.steps
                * env.unwrapped.step_dt
                / (2.0 * math.pi),
                "drop_events_estimate": round(means["rotate/drop_rate"] * args.steps * args.num_envs),
                "object_mass_kg": float(wp.to_torch(env.unwrapped.object.data.body_mass).flatten()[0].item()),
            }
        finally:
            raw_env.close()

        payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
        if args.output is not None:
            output = args.output.expanduser().resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(payload)
        print("ALLEGRO_EVALUATION_RESULT " + json.dumps(report, allow_nan=False), flush=True)
        if not report["all_finite"]:
            raise RuntimeError("Evaluation produced non-finite observations or rewards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
