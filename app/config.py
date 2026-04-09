"""Application configuration helpers.

This module is responsible for:
- reading environment variables
- loading values from a local .env file
- validating required settings
- building safe defaults
- masking sensitive values before they are logged
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


def _load_local_dotenv() -> None:
    """Load environment variables from the project-level .env file.

    A .env file is a simple local file where developers can store environment
    variables during development. It should not be committed to source control
    because it may contain secrets or private account details.

    We use `override=False` so real process environment variables always win.
    That makes local development convenient without changing production-safe
    behavior.
    """

    project_root = Path(__file__).resolve().parent.parent
    dotenv_path = project_root / ".env"

    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=False)


def _to_bool(value: str | None, default: bool = False) -> bool:
    """Convert common string values into a boolean."""
    if value is None:
        return default

    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def _clean_env(name: str, default: str | None = None) -> str | None:
    """Read an environment variable and normalize blank values to None."""
    value = os.getenv(name, default)

    if value is None:
        return None

    cleaned = value.strip()
    return cleaned or None


def mask_secret(value: str | None) -> str:
    """Hide most of a secret so it can be logged safely."""
    if not value:
        return "<not-set>"

    if len(value) <= 4:
        return "*" * len(value)

    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"


@dataclass(slots=True)
class Settings:
    """All application settings in one place."""

    app_name: str
    app_env: str
    debug: bool
    dry_run: bool
    log_level: str
    data_dir: Path
    database_path: Path
    amazon_associate_tag: str
    facebook_page_id: str | None
    facebook_page_access_token: str | None

    def safe_log_values(self) -> dict[str, str]:
        """Return a version of the settings that is safe to log."""
        return {
            "app_name": self.app_name,
            "app_env": self.app_env,
            "debug": str(self.debug),
            "dry_run": str(self.dry_run),
            "log_level": self.log_level,
            "data_dir": str(self.data_dir),
            "database_path": str(self.database_path),
            "amazon_associate_tag": mask_secret(self.amazon_associate_tag),
            "facebook_page_id": mask_secret(self.facebook_page_id),
            "facebook_page_access_token": mask_secret(self.facebook_page_access_token),
        }


def load_settings() -> Settings:
    """Load and validate application settings.

    Phase 1 only requires:
    - AMAZON_ASSOCIATE_TAG
    """

    # Load local development variables before reading from os.environ.
    # If the file does not exist, the app simply continues as normal.
    _load_local_dotenv()

    project_root = Path(__file__).resolve().parent.parent
    default_data_dir = project_root / "data"

    app_name = _clean_env("APP_NAME", "amazon-affiliate-content-agent") or "amazon-affiliate-content-agent"
    app_env = _clean_env("APP_ENV", "development") or "development"
    log_level = (_clean_env("LOG_LEVEL", "INFO") or "INFO").upper()
    debug = _to_bool(_clean_env("DEBUG"), default=False)
    dry_run = _to_bool(_clean_env("DRY_RUN"), default=True)

    data_dir_raw = _clean_env("DATA_DIR")
    database_path_raw = _clean_env("DATABASE_PATH")
    amazon_associate_tag = _clean_env("AMAZON_ASSOCIATE_TAG")
    facebook_page_id = _clean_env("FACEBOOK_PAGE_ID")
    facebook_page_access_token = _clean_env("FACEBOOK_PAGE_ACCESS_TOKEN")

    missing_fields: list[str] = []

    if not amazon_associate_tag:
        missing_fields.append(
            "AMAZON_ASSOCIATE_TAG is required. Add your Amazon Associates tracking tag to the environment."
        )

    if missing_fields:
        message = "Configuration is incomplete:\n- " + "\n- ".join(missing_fields)
        raise ConfigError(message)

    data_dir = Path(data_dir_raw) if data_dir_raw else default_data_dir
    database_path = Path(database_path_raw) if database_path_raw else data_dir / "agent.db"

    return Settings(
        app_name=app_name,
        app_env=app_env,
        debug=debug,
        dry_run=dry_run,
        log_level=log_level,
        data_dir=data_dir,
        database_path=database_path,
        amazon_associate_tag=amazon_associate_tag,
        facebook_page_id=facebook_page_id,
        facebook_page_access_token=facebook_page_access_token,
    )
