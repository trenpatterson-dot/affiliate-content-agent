"""Disclosure helpers for affiliate draft content.

This module keeps disclosure handling in one place so draft generation
can stay consistent and easy to update later.
"""

from __future__ import annotations


DEFAULT_DISCLOSURE_TEXT = "#ad #affiliate I may earn a commission from qualifying purchases."


def get_default_disclosure() -> str:
    """Return the default disclosure text used in all drafts."""

    return DEFAULT_DISCLOSURE_TEXT


def build_compliance_notes() -> list[str]:
    """Return simple compliance reminders that can travel with a draft."""

    return [
        "Include the disclosure line when publishing or reviewing this draft.",
        "Use plain, factual language and avoid unsupported marketing claims.",
        "Confirm price and product details again before publishing because they may change over time.",
    ]
