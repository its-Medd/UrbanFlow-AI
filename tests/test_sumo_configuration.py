from pathlib import Path

from agentsumo_mcp.settings import settings


def test_explicit_sumo_home_takes_precedence(monkeypatch, tmp_path):
    monkeypatch.setenv('SUMO_HOME', str(tmp_path))
    monkeypatch.setattr(settings.shutil, 'which', lambda _: '/other/bin/sumo')
    assert settings._load_sumo_home() == str(tmp_path)


def test_sumo_can_be_discovered_from_path(monkeypatch, tmp_path):
    monkeypatch.delenv('SUMO_HOME', raising=False)
    # Redirect the module's legacy-file lookup to an isolated source layout.
    module_path = tmp_path/'repo'/'agentsumo_mcp'/'settings'/'settings.py'
    module_path.parent.mkdir(parents=True)
    module_path.touch()
    monkeypatch.setattr(settings, '__file__', str(module_path))
    executable = tmp_path/'installed'/'bin'/'sumo'
    monkeypatch.setattr(settings.shutil, 'which', lambda _: str(executable))
    assert settings._load_sumo_home() == str(executable.parent.parent)


def test_missing_sumo_does_not_assume_a_developer_machine(monkeypatch, tmp_path):
    monkeypatch.delenv('SUMO_HOME', raising=False)
    module_path = tmp_path/'repo'/'agentsumo_mcp'/'settings'/'settings.py'
    module_path.parent.mkdir(parents=True)
    module_path.touch()
    monkeypatch.setattr(settings, '__file__', str(module_path))
    monkeypatch.setattr(settings.shutil, 'which', lambda _: None)
    assert settings._load_sumo_home() == ''
