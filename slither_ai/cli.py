"""Command-line entry points for environment validation and PPO experiments."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from slither_ai.envs import SnakeEnv


def smoke(seed: int = 7, steps: int = 500) -> None:
    env = SnakeEnv()
    obs, info = env.reset(seed=seed)
    total_reward = 0.0
    rng = np.random.default_rng(seed)
    try:
        for _ in range(steps):
            obs, reward, terminated, truncated, info = env.step(int(rng.integers(3)))
            total_reward += reward
            if terminated or truncated:
                obs, info = env.reset()
        print(
            f"smoke_ok steps={steps} total_reward={total_reward:.3f} "
            f"last_length={info['length']} last_food={info['food_eaten']}"
        )
    finally:
        env.close()


def play(seed: int = 7, policy: str = "random", action: int = 1) -> None:
    """Run one interactive episode using random or fixed relative steering."""
    if policy not in ("random", "fixed"):
        raise ValueError("policy must be 'random' or 'fixed'")
    if action not in (0, 1, 2):
        raise ValueError("action must be 0 (left), 1 (straight), or 2 (right)")

    env = SnakeEnv(render_mode="human")
    try:
        _, info = env.reset(seed=seed)
        env.action_space.seed(seed)
        while env.render_mode == "human":
            selected_action = env.action_space.sample() if policy == "random" else action
            _, _, terminated, truncated, info = env.step(selected_action)
            if terminated or truncated or env.render_mode != "human":
                break
        print(
            f"play_finished steps={info['steps']} length={info['length']} "
            f"food={info['food_eaten']}"
        )
    except KeyboardInterrupt:
        print("play_stopped reason=keyboard_interrupt")
    finally:
        env.close()


def train(timesteps: int, output: str, seed: int, device: str) -> None:
    from stable_baselines3 import PPO
    from stable_baselines3.common.monitor import Monitor

    env = Monitor(SnakeEnv())
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        seed=seed,
        device=device,
        tensorboard_log="runs/tensorboard",
        n_steps=1024,
        batch_size=256,
        learning_rate=3e-4,
        gamma=0.99,
    )
    model.learn(total_timesteps=timesteps, tb_log_name="ppo_snake")
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(path))
    print(f"saved_model={path.with_suffix('.zip')}")
    env.close()


def evaluate(model_path: str, episodes: int, seed: int, device: str) -> None:
    from stable_baselines3 import PPO

    model = PPO.load(model_path, device=device)
    env = SnakeEnv()
    returns, lengths, food = [], [], []
    try:
        for episode in range(episodes):
            obs, _ = env.reset(seed=seed + episode)
            done = False
            total = 0.0
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(int(action))
                total += reward
                done = terminated or truncated
            returns.append(total)
            lengths.append(info["length"])
            food.append(info["food_eaten"])
        print(
            f"episodes={episodes} return_mean={np.mean(returns):.3f} "
            f"return_std={np.std(returns):.3f} length_mean={np.mean(lengths):.2f} "
            f"food_mean={np.mean(food):.2f}"
        )
    finally:
        env.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="slither-ai")
    sub = parser.add_subparsers(dest="command", required=True)
    p_smoke = sub.add_parser("smoke")
    p_smoke.add_argument("--seed", type=int, default=7)
    p_smoke.add_argument("--steps", type=int, default=500)
    p_train = sub.add_parser("train")
    p_train.add_argument("--timesteps", type=int, default=100_000)
    p_train.add_argument("--output", default="checkpoints/ppo_baseline")
    p_train.add_argument("--seed", type=int, default=7)
    p_train.add_argument("--device", default="auto")
    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--model", default="checkpoints/ppo_baseline.zip")
    p_eval.add_argument("--episodes", type=int, default=20)
    p_eval.add_argument("--seed", type=int, default=10_000)
    p_eval.add_argument("--device", default="auto")
    p_play = sub.add_parser("play", help="play the local environment with a visual window")
    p_play.add_argument("--policy", choices=("random", "fixed"), default="random")
    p_play.add_argument("--action", type=int, choices=(0, 1, 2), default=1)
    p_play.add_argument("--seed", type=int, default=7)

    args = parser.parse_args(argv)
    if args.command == "smoke":
        smoke(args.seed, args.steps)
    elif args.command == "train":
        train(args.timesteps, args.output, args.seed, args.device)
    elif args.command == "evaluate":
        evaluate(args.model, args.episodes, args.seed, args.device)
    else:
        play(args.seed, args.policy, args.action)


if __name__ == "__main__":
    main()
