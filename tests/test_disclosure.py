"""Tests for disclosure helpers."""

from __future__ import annotations

from app.disclosure import build_compliance_notes, get_default_disclosure


def test_get_default_disclosure_returns_expected_text():
    """Proves the project has one consistent default disclosure string."""

    assert get_default_disclosure() == "#ad #affiliate I may earn a commission from qualifying purchases."


def test_build_compliance_notes_returns_readable_notes():
    """Proves draft helpers can attach human-readable compliance reminders."""

    notes = build_compliance_notes()

    assert len(notes) >= 3
    assert all(isinstance(note, str) for note in notes)
