"""Compliance helpers for affiliate content drafts.

This module helps us review drafts before publishing or sharing them.
It supports a compliance-aware workflow, but it does not replace legal
review or platform-specific policy review.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from app.models import ProductDraft


BLOCKED_HYPE_PHRASES = [
    "best",
    "hottest",
    "viral",
    "top selling",
    "lowest price ever",
]

TIME_SENSITIVE_PROMOTION_PHRASES = [
    "limited time",
    "expires soon",
    "today only",
]

UNSUPPORTED_PRICE_OR_AVAILABILITY_PHRASES = [
    "in stock now",
    "always in stock",
    "guaranteed lowest price",
    "lowest price",
    "won't last long",
    "selling out fast",
]


@dataclass(slots=True)
class ComplianceResult:
    """Structured compliance review output for one draft."""

    draft_id: str
    passed: bool
    reasons: list[str]
    checklist: dict[str, bool]

    @property
    def status(self) -> str:
        """Return a simple PASS or FAIL label."""

        return "PASS" if self.passed else "FAIL"


def check_draft_compliance(
    draft: ProductDraft,
    recheck_timestamp_utc: str | None = None,
) -> ComplianceResult:
    """Run all compliance checks for a draft."""

    reasons: list[str] = []
    checklist = {
        "disclosure_present": check_disclosure_present(draft, reasons),
        "affiliate_link_present": check_affiliate_link_present(draft, reasons),
        "required_product_data_present": check_required_product_data(draft, reasons),
        "no_blocked_hype_claims": check_hype_language(draft, reasons),
        "promotion_wording_is_supported": check_promotion_wording(draft, reasons, recheck_timestamp_utc),
        "price_and_availability_wording_is_supported": check_price_availability_wording(draft, reasons),
    }

    passed = all(checklist.values())
    return ComplianceResult(
        draft_id=draft.draft_id,
        passed=passed,
        reasons=reasons,
        checklist=checklist,
    )


def check_disclosure_present(draft: ProductDraft, reasons: list[str]) -> bool:
    """Check that the required disclosure text is present."""

    actual_disclosure = (draft.disclosure_text or "").strip()

    # This supports a compliance-aware workflow while staying flexible.
    # Exact disclosure wording may evolve over time, so this check only
    # requires that a disclosure is present rather than matching one
    # exact string forever.
    if not actual_disclosure:
        reasons.append("Disclosure is missing.")
        return False

    return True


def check_affiliate_link_present(draft: ProductDraft, reasons: list[str]) -> bool:
    """Check that an affiliate link exists and looks like a URL."""

    affiliate_url = (draft.affiliate_url or "").strip()

    if not affiliate_url:
        reasons.append("Affiliate link is missing.")
        return False

    parsed = urlparse(affiliate_url)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        reasons.append("Affiliate link is present but malformed.")
        return False

    return True


def check_required_product_data(draft: ProductDraft, reasons: list[str]) -> bool:
    """Check for missing draft fields that usually come from product data."""

    missing_fields: list[str] = []

    if not (draft.product_id or "").strip():
        missing_fields.append("product_id")

    if not (draft.title or "").strip():
        missing_fields.append("title")

    if not (draft.caption or "").strip():
        missing_fields.append("caption")

    if missing_fields:
        reasons.append(
            "Draft is missing required product-related content: " + ", ".join(missing_fields) + "."
        )
        return False

    return True


def check_hype_language(draft: ProductDraft, reasons: list[str]) -> bool:
    """Block unsupported hype language in titles or captions."""

    text_to_check = build_publishable_text_for_review(draft)
    found_phrases = _find_phrases(text_to_check, BLOCKED_HYPE_PHRASES)

    if found_phrases:
        reasons.append(
            "Draft uses blocked hype wording: " + ", ".join(found_phrases) + "."
        )
        return False

    return True


def check_promotion_wording(
    draft: ProductDraft,
    reasons: list[str],
    recheck_timestamp_utc: str | None,
) -> bool:
    """Block time-sensitive promotion language unless a recheck timestamp exists."""

    text_to_check = build_publishable_text_for_review(draft)
    found_phrases = _find_phrases(text_to_check, TIME_SENSITIVE_PROMOTION_PHRASES)

    if not found_phrases:
        return True

    if recheck_timestamp_utc and recheck_timestamp_utc.strip():
        return True

    reasons.append(
        "Draft uses time-sensitive promotion wording without a recheck timestamp: "
        + ", ".join(found_phrases)
        + "."
    )
    return False


def check_price_availability_wording(draft: ProductDraft, reasons: list[str]) -> bool:
    """Block unsupported certainty claims about price or availability."""

    text_to_check = build_publishable_text_for_review(draft)
    found_phrases = _find_phrases(text_to_check, UNSUPPORTED_PRICE_OR_AVAILABILITY_PHRASES)

    if found_phrases:
        reasons.append(
            "Draft uses unsupported price or availability wording: "
            + ", ".join(found_phrases)
            + "."
        )
        return False

    return True


def build_publishable_text_for_review(draft: ProductDraft) -> str:
    """Combine caption and disclosure for full-text review checks.

    This helper makes it easy to review the final user-facing text block
    if later checks need to inspect the disclosure alongside the caption.
    """

    return f"{draft.title} {draft.caption} {draft.disclosure_text}".lower()


def _find_phrases(text: str, phrases: list[str]) -> list[str]:
    """Return the phrases that appear in the text."""

    return [phrase for phrase in phrases if phrase in text]
