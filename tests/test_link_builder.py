"""Tests for affiliate link building."""

from __future__ import annotations

import pytest

import app.config as config_module
from app.link_builder import LinkBuilderError, build_affiliate_url, build_affiliate_url_with_tag


def test_build_affiliate_url_with_tag_preserves_query_and_fragment():
    """Proves link building keeps existing query values and URL fragments."""

    result = build_affiliate_url_with_tag(
        "https://example.com/item?ref=abc#details",
        "yourtag-20",
    )

    assert result.original_url == "https://example.com/item?ref=abc#details"
    assert "ref=abc" in result.affiliate_url
    assert "tag=yourtag-20" in result.affiliate_url
    assert result.affiliate_url.endswith("#details")


def test_build_affiliate_url_replaces_existing_tag():
    """Proves an old tag is replaced instead of duplicated."""

    result = build_affiliate_url_with_tag(
        "https://example.com/item?tag=oldtag-20&ref=abc",
        "newtag-20",
    )

    assert "tag=newtag-20" in result.affiliate_url
    assert "oldtag-20" not in result.affiliate_url


def test_build_affiliate_url_reads_tag_from_config(monkeypatch):
    """Proves the public helper uses the centralized config layer."""

    monkeypatch.setattr(config_module, "_load_local_dotenv", lambda: None)
    monkeypatch.setenv("AMAZON_ASSOCIATE_TAG", "yourtag-20")

    result = build_affiliate_url("https://example.com/item")

    assert result.affiliate_tag_used == "yourtag-20"


def test_build_affiliate_url_rejects_empty_urls():
    """Proves the helper raises a friendly error for empty input."""

    with pytest.raises(LinkBuilderError) as error:
        build_affiliate_url_with_tag("", "yourtag-20")

    assert "Product URL is empty" in str(error.value)
