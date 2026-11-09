from slither_ai.cli import smoke


def test_smoke_runs(capsys):
    smoke(seed=2, steps=25)
    assert "smoke_ok" in capsys.readouterr().out
