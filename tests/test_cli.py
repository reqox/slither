from slither_ai import cli


class FakeActionSpace:
    def __init__(self, action=2):
        self.action = action
        self.seed_value = None

    def seed(self, seed):
        self.seed_value = seed

    def sample(self):
        return self.action


class FakeEnv:
    def __init__(self, *, render_mode, interrupt=False):
        assert render_mode == "human"
        self.render_mode = render_mode
        self.action_space = FakeActionSpace()
        self.interrupt = interrupt
        self.actions = []
        self.closed = False
        self.reset_seed = None

    def reset(self, *, seed):
        self.reset_seed = seed
        return None, {"steps": 0, "length": 8, "food_eaten": 0}

    def step(self, action):
        if self.interrupt:
            raise KeyboardInterrupt
        self.actions.append(action)
        self.render_mode = None
        return None, 0.0, False, False, {"steps": 1, "length": 8, "food_eaten": 0}

    def close(self):
        self.closed = True


def test_play_parser_dispatches_random_policy(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "play", lambda *args: calls.append(args))
    cli.main(["play", "--policy", "random", "--seed", "19"])
    assert calls == [(19, "random", 1)]


def test_play_parser_dispatches_fixed_action(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "play", lambda *args: calls.append(args))
    cli.main(["play", "--policy", "fixed", "--action", "2"])
    assert calls == [(7, "fixed", 2)]


def test_play_uses_fixed_action_and_closes_when_window_closes(monkeypatch, capsys):
    env = FakeEnv(render_mode="human")
    monkeypatch.setattr(cli, "SnakeEnv", lambda **kwargs: env)
    cli.play(seed=11, policy="fixed", action=0)
    assert env.reset_seed == 11
    assert env.action_space.seed_value == 11
    assert env.actions == [0]
    assert env.closed
    assert "play_finished" in capsys.readouterr().out


def test_play_uses_random_action(monkeypatch):
    env = FakeEnv(render_mode="human")
    monkeypatch.setattr(cli, "SnakeEnv", lambda **kwargs: env)
    cli.play(policy="random")
    assert env.actions == [2]
    assert env.closed


def test_play_handles_keyboard_interrupt_and_closes(monkeypatch, capsys):
    env = FakeEnv(render_mode="human", interrupt=True)
    monkeypatch.setattr(cli, "SnakeEnv", lambda **kwargs: env)
    cli.play()
    assert env.closed
    assert "keyboard_interrupt" in capsys.readouterr().out


def test_smoke_runs(capsys):
    cli.smoke(seed=2, steps=25)
    assert "smoke_ok" in capsys.readouterr().out
