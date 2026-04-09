"""Application entry point for Phase 1."""

from __future__ import annotations

import sys

from app.config import ConfigError, load_settings
from app.db import initialize_database
from app.logger import setup_logger


def main() -> int:
    """Run the application startup sequence."""
    try:
        settings = load_settings()
    except ConfigError as error:
        print(error)
        return 1

    logger = setup_logger(settings.log_level)

    logger.info("Starting %s in %s mode", settings.app_name, settings.app_env)
    logger.info("Configuration loaded: %s" % settings.safe_log_values())

    try:
        initialize_database(settings.database_path)
    except Exception as error:  # pragma: no cover - defensive startup guard
        logger.error("Database initialization failed: %s", error)
        return 1

    logger.info("Database ready at %s", settings.database_path)
    print("Agent Ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
