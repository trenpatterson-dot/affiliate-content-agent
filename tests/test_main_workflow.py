"""Smoke tests for the current app.main startup flow."""

from __future__ import annotations

import app.config as config_module
from app import main as main_module


def test_main_starts_successfully_with_temp_database(monkeypatch, tmp_path, capsys):
    """Proves the current main entry point can start cleanly with test settings."""

    database_path = tmp_path / "agent.db"

    monkeypatch.setattr(config_module, "_load_local_dotenv", lambda: None)
    monkeypatch.setenv("AMAZON_ASSOCIATE_TAG", "yourtag-20")
    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    monkeypatch.setenv("DRY_RUN", "true")

    result = main_module.main()
    captured = capsys.readouterr()

    assert result == 0
    assert (
        "Workflow Summary" in captured.out
        or "total products loaded" in captured.out
        or "Agent Ready" in captured.out
    )
    assert database_path.exists()


def test_main_returns_error_when_config_is_incomplete(monkeypatch, capsys):
    """Proves startup exits cleanly with a friendly config error."""

    monkeypatch.setattr(config_module, "_load_local_dotenv", lambda: None)
    monkeypatch.delenv("AMAZON_ASSOCIATE_TAG", raising=False)

    result = main_module.main()
    captured = capsys.readouterr()

    assert result == 1
    assert "Configuration is incomplete" in captured.out
