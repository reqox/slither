import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from slither_ai.envs import SnakeEnv


def test_gymnasium_env_checker():
    check_env(SnakeEnv(), skip_render_check=True)


def test_reset_is_deterministic_for_same_seed():
    env = SnakeEnv()
    obs_a, info_a = env.reset(seed=123)
    obs_b, info_b = env.reset(seed=123)
    np.testing.assert_array_equal(obs_a, obs_b)
    np.testing.assert_array_equal(info_a["position"], info_b["position"])
    np.testing.assert_array_equal(info_a["food_position"], info_b["food_position"])
    assert env._food.tolist()  # food is initialized


def test_step_contract_and_observation_bounds():
    env = SnakeEnv(max_steps=3)
    obs, _ = env.reset(seed=1)
    assert env.observation_space.contains(obs)
    for _ in range(3):
        obs, reward, terminated, truncated, info = env.step(1)
        assert env.observation_space.contains(obs)
        assert np.isfinite(reward)
        if terminated or truncated:
            break
    assert terminated or truncated
    assert info["steps"] <= 3


def test_invalid_action_rejected():
    env = SnakeEnv()
    env.reset(seed=1)
    with pytest.raises(ValueError):
        env.step(9)


@pytest.mark.parametrize("parameter", ["arena_size", "speed", "turn_rate"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_physics_parameters_rejected(parameter, value):
    with pytest.raises(ValueError, match="must be finite"):
        SnakeEnv(**{parameter: value})
