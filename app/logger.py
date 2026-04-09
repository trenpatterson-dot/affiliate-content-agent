"""Logging helpers for the application."""

from __future__ import annotations

import logging
import re


class SensitiveDataFilter(logging.Filter):
    """Mask obvious secret-like values before they reach the console."""

    _patterns = [
        re.compile(r"(sk-[A-Za-z0-9_-]{8,})"),
        re.compile(r"(AKIA[0-9A-Z]{8,})"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Update the log message in-place with masked values."""
        if isinstance(record.msg, str):
            record.msg = self._mask_text(record.msg)

        if record.args:
            record.args = tuple(
                self._mask_text(arg) if isinstance(arg, str) else arg for arg in record.args
            )

        return True

    def _mask_text(self, text: str) -> str:
        masked = text

        for pattern in self._patterns:
            masked = pattern.sub(self._replace_secret, masked)

        return masked

    @staticmethod
    def _replace_secret(match: re.Match[str]) -> str:
        secret = match.group(0)

        if len(secret) <= 6:
            return "*" * len(secret)

        return f"{secret[:2]}{'*' * (len(secret) - 4)}{secret[-2:]}"


def setup_logger(level: str = "INFO") -> logging.Logger:
    """Configure and return the main application logger."""
    logger = logging.getLogger("amazon_affiliate_agent")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler.addFilter(SensitiveDataFilter())

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
