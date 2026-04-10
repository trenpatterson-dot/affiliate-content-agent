"""Tests for draft generation helpers."""

from __future__ import annotations

from app.disclosure import get_default_disclosure
from app.drafts import (
    create_deal_post,
    create_simple_roundup_entry,
    create_why_it_is_useful_post,
    format_publishable_text,
    generate_all_draft_types,
)


def test_generate_all_draft_types_builds_three_supported_drafts(monkeypatch, sample_product):
    """Proves one product produces all three required draft types."""

    monkeypatch.setenv("AMAZON_ASSOCIATE_TAG", "yourtag-20")

    drafts = generate_all_draft_types(sample_product)

    assert len(drafts) == 3
    assert {draft.draft_type for draft in drafts} == {
        "deal_post",
        "why_it_is_useful_post",
        "simple_roundup_entry",
    }


def test_draft_generation_includes_affiliate_link_and_disclosure(monkeypatch, sample_product):
    """Proves generated drafts carry both an affiliate URL and disclosure text."""

    monkeypatch.setenv("AMAZON_ASSOCIATE_TAG", "yourtag-20")

    draft = create_deal_post(sample_product)

    assert "tag=yourtag-20" in draft.affiliate_url
    assert draft.disclosure_text == get_default_disclosure()


def test_format_publishable_text_combines_caption_and_disclosure(monkeypatch, sample_product):
    """Proves publishable text formatting keeps disclosure separate until final output."""

    monkeypatch.setenv("AMAZON_ASSOCIATE_TAG", "yourtag-20")

    draft = create_why_it_is_useful_post(sample_product)
    publishable_text = format_publishable_text(draft)

    assert draft.caption in publishable_text
    assert draft.disclosure_text in publishable_text


def test_simple_roundup_entry_stays_plain(monkeypatch, sample_product):
    """Proves roundup entries use the expected simple draft type."""

    monkeypatch.setenv("AMAZON_ASSOCIATE_TAG", "yourtag-20")

    draft = create_simple_roundup_entry(sample_product)

    assert draft.draft_type == "simple_roundup_entry"
    assert draft.title == sample_product.title
