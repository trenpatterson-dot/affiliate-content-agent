"""Tests for configuration loading and validation."""

from __future__ import annotations

import pytest

import app.config as config_module
from app.config import ConfigError, load_settings, mask_secret


def test_load_settings_requires_amazon_tag(monkeypatch):
    """Proves config loading fails with a friendly message when the tag is missing."""

    monkeypatch.setattr(config_module, "_load_local_dotenv", lambda: None)
    monkeypatch.delenv("AMAZON_ASSOCIATE_TAG", raising=False)
    monkeypatch.delenv("DATA_DIR", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("DRY_RUN", raising=False)

    with pytest.raises(ConfigError) as error:
        load_settings()

    assert "AMAZON_ASSOCIATE_TAG is required" in str(error.value)


def test_load_settings_uses_safe_defaults_and_env_values(monkeypatch, tmp_path):
    """Proves config loads defaults cleanly and respects explicit overrides."""

    database_path = tmp_path / "custom.db"

    monkeypatch.setattr(config_module, "_load_local_dotenv", lambda: None)
    monkeypatch.setenv("AMAZON_ASSOCIATE_TAG", "yourtag-20")
    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DRY_RUN", "false")

    settings = load_settings()

    assert settings.app_name == "amazon-affiliate-content-agent"
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert settings.debug is True
    assert settings.dry_run is False
    assert settings.database_path == database_path


def test_mask_secret_hides_most_of_a_value():
    """Proves secret masking keeps logs readable without exposing the full value."""

    assert mask_secret("yourtag-20").startswith("yo")
    assert mask_secret("yourtag-20").endswith("20")
    assert mask_secret(None) == "<not-set>"
