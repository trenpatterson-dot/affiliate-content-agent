"""Tests for draft compliance checks."""

from __future__ import annotations

from app.compliance import check_draft_compliance
from app.disclosure import get_default_disclosure
from app.models import ProductDraft


def _make_draft(**overrides) -> ProductDraft:
    """Build a small reusable draft object for compliance tests."""

    data = {
        "draft_id": "draft-001",
        "product_id": "product-001",
        "draft_type": "deal_post",
        "title": "Useful keyboard option",
        "caption": "Useful keyboard option. Link: https://example.com/item?tag=yourtag-20",
        "affiliate_url": "https://example.com/item?tag=yourtag-20",
        "disclosure_text": get_default_disclosure(),
        "compliance_notes": ["Check before publishing."],
    }
    data.update(overrides)
    return ProductDraft(**data)


def test_compliance_passes_for_plain_compliant_draft():
    """Proves a normal plain-language draft can pass the compliance checks."""

    result = check_draft_compliance(_make_draft())

    assert result.passed is True
    assert result.status == "PASS"


def test_compliance_fails_when_disclosure_is_missing():
    """Proves missing disclosure text blocks the draft."""

    result = check_draft_compliance(_make_draft(disclosure_text=""))

    assert result.passed is False
    assert "Disclosure is missing." in result.reasons


def test_compliance_fails_for_blocked_hype_phrases():
    """Proves blocked hype wording is detected in the full publishable text."""

    result = check_draft_compliance(_make_draft(title="Best keyboard right now"))

    assert result.passed is False
    assert any("blocked hype wording" in reason.lower() for reason in result.reasons)


def test_compliance_fails_for_time_sensitive_promotion_without_recheck():
    """Proves urgency wording needs a recheck timestamp."""

    result = check_draft_compliance(_make_draft(caption="Today only deal. Link: https://example.com/item"))

    assert result.passed is False
    assert any("recheck timestamp" in reason.lower() for reason in result.reasons)
