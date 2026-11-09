"""Small deterministic Slither-like environment for the first RL baseline.

This is deliberately a controllable research environment, not a protocol/client
implementation of the official Slither.io game.
"""
from __future__ import annotations

import math

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class SnakeEnv(gym.Env):
    """Continuous 2D arena with food, walls, and a single growing snake.

    Actions: 0 = turn left, 1 = straight, 2 = turn right.
    Observation (10 floats): heading cos/sin, food-relative x/y, food distance,
    normalized distances to all four walls, normalized body length.
    """

    metadata = {"render_modes": ["human"], "render_fps": 12}

    def __init__(
        self,
        arena_size: float = 500.0,
        speed: float = 5.0,
        turn_rate: float = 0.22,
        initial_length: int = 8,
        max_steps: int = 2_000,
        render_mode: str | None = None,
    ) -> None:
        super().__init__()
        if render_mode not in (None, "human"):
            raise ValueError("render_mode must be None or human")
        self.render_mode = render_mode
        self._screen = None
        self._clock = None
        if not all(math.isfinite(value) for value in (arena_size, speed, turn_rate)):
            raise ValueError("arena_size, speed, and turn_rate must be finite")
        if arena_size <= 40 or speed <= 0 or turn_rate <= 0:
            raise ValueError("arena_size must exceed 40; speed and turn_rate must be positive")
        if initial_length < 3 or max_steps < 1:
            raise ValueError("initial_length must be >= 3 and max_steps must be >= 1")
        self.arena_size = float(arena_size)
        self.speed = float(speed)
        self.turn_rate = float(turn_rate)
        self.initial_length = int(initial_length)
        self.max_steps = int(max_steps)
        if self.arena_size / 2 <= self.speed * (self.initial_length - 1) + 1:
            raise ValueError("arena is too small for the initial snake length")
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(
            low=np.array([-1, -1, -1, -1, 0, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.ones(10, dtype=np.float32),
            dtype=np.float32,
        )
        self._head = np.zeros(2, dtype=np.float64)
        self._angle = 0.0
        self._body: list[np.ndarray] = []
        self._food = np.zeros(2, dtype=np.float64)
        self._target_length = self.initial_length
        self._steps = 0
        self._food_eaten = 0

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict | None = None,
    ) -> tuple[np.ndarray, dict]:
        super().reset(seed=seed)
        del options
        center = self.arena_size / 2
        self._head = np.array([center, center], dtype=np.float64)
        self._angle = float(self.np_random.uniform(-np.pi, np.pi))
        direction = np.array([np.cos(self._angle), np.sin(self._angle)])
        self._body = [
            self._head - direction * self.speed * i for i in range(self.initial_length)
        ]
        self._target_length = self.initial_length
        self._steps = 0
        self._food_eaten = 0
        self._spawn_food()
        if self.render_mode == "human":
            self.render()
        return self._observation(), self._info()

    def step(self, action: int):
        if not self.action_space.contains(action):
            raise ValueError(f"invalid action: {action}")
        self._steps += 1
        previous_food_distance = float(np.linalg.norm(self._food - self._head))
        if action == 0:
            self._angle += self.turn_rate
        elif action == 2:
            self._angle -= self.turn_rate

        direction = np.array([np.cos(self._angle), np.sin(self._angle)])
        self._head = self._head + direction * self.speed
        self._body.insert(0, self._head.copy())
        self._body = self._body[: self._target_length]

        current_food_distance = float(np.linalg.norm(self._food - self._head))
        reward = 0.01 + (previous_food_distance - current_food_distance) * 0.02
        terminated = False
        reason = None
        if np.any(self._head <= 0) or np.any(self._head >= self.arena_size):
            terminated, reason = True, "wall"
        elif self._hits_body():
            terminated, reason = True, "self_collision"

        if not terminated and np.linalg.norm(self._head - self._food) <= self.speed * 1.5:
            self._target_length += 5
            self._food_eaten += 1
            reward += 1.0
            self._spawn_food()

        truncated = self._steps >= self.max_steps and not terminated
        if terminated:
            reward -= 1.0

        info = self._info()
        info["termination_reason"] = reason
        if self.render_mode == "human":
            self.render()
        return self._observation(), float(reward), terminated, truncated, info

    def _hits_body(self) -> bool:
        # Ignore the newest points near the head and the tail that just vacated.
        if len(self._body) < 10:
            return False
        head = self._head
        return any(np.linalg.norm(head - point) < self.speed * 0.8 for point in self._body[8:-1])

    def _spawn_food(self) -> None:
        margin = 20.0
        for _ in range(100):
            candidate = self.np_random.uniform(margin, self.arena_size - margin, size=2)
            if all(np.linalg.norm(candidate - p) > self.speed * 4 for p in self._body):
                self._food = candidate
                return
        self._food = self.np_random.uniform(margin, self.arena_size - margin, size=2)

    def _observation(self) -> np.ndarray:
        half = self.arena_size / 2
        delta = self._food - self._head
        distance = min(float(np.linalg.norm(delta)) / (self.arena_size * np.sqrt(2)), 1.0)
        return np.array(
            [
                np.cos(self._angle),
                np.sin(self._angle),
                np.clip(delta[0] / half, -1, 1),
                np.clip(delta[1] / half, -1, 1),
                distance,
                np.clip(self._head[0] / self.arena_size, 0, 1),
                np.clip((self.arena_size - self._head[0]) / self.arena_size, 0, 1),
                np.clip(self._head[1] / self.arena_size, 0, 1),
                np.clip((self.arena_size - self._head[1]) / self.arena_size, 0, 1),
                np.clip(self._target_length / (self.initial_length + 100), 0, 1),
            ],
            dtype=np.float32,
        )

    def _info(self) -> dict:
        return {
            "steps": self._steps,
            "food_eaten": self._food_eaten,
            "length": self._target_length,
            "position": self._head.copy(),
            "food_position": self._food.copy(),
        }


    def render(self) -> None:
        """Draw the current state. Pygame is imported only for human rendering."""
        if self.render_mode != "human":
            return
        try:
            import pygame
        except ImportError as exc:
            raise ImportError(
                'Human rendering requires Pygame. Install with '
                'python -m pip install -e ".[visualization]".'
            ) from exc

        window_size = 800
        if self._screen is None:
            pygame.init()
            self._screen = pygame.display.set_mode((window_size, window_size))
            pygame.display.set_caption("Slither AI - Local Environment")
            self._clock = pygame.time.Clock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return

        scale = window_size / self.arena_size
        self._screen.fill((22, 27, 34))
        pygame.draw.rect(self._screen, (95, 105, 115), (0, 0, window_size, window_size), 2)
        food = tuple(int(v * scale) for v in self._food)
        pygame.draw.circle(self._screen, (245, 190, 65), food, 7)

        points = [tuple(int(v * scale) for v in point) for point in self._body]
        if len(points) > 1:
            pygame.draw.lines(self._screen, (65, 180, 115), False, points, 12)
        if points:
            pygame.draw.circle(self._screen, (105, 225, 150), points[0], 8)

        pygame.display.flip()
        self._clock.tick(self.metadata["render_fps"])

    def close(self) -> None:
        """Release the optional Pygame window."""
        if self._screen is not None:
            import pygame

            pygame.display.quit()
            pygame.quit()
            self._screen = None
            self._clock = None

