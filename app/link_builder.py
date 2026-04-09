"""Helpers for building affiliate-tagged product links.

This module keeps the first version of link building simple:
- read the affiliate tag from environment variables only
- validate inputs with friendly errors
- preserve existing query parameters
- avoid any external API calls

The goal is to keep this easy to test and easy to understand.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from app.config import ConfigError, load_settings


class LinkBuilderError(Exception):
    """Raised when a product URL or affiliate tag is missing or invalid."""


@dataclass(slots=True)
class AffiliateLinkResult:
    """Structured result returned by the link builder."""

    original_url: str
    affiliate_url: str
    affiliate_tag_used: str


def build_affiliate_url(product_url: str) -> AffiliateLinkResult:
    """Build an affiliate-tagged URL from a product URL.

    The affiliate tag is loaded through the shared config layer so
    configuration stays centralized in one place.
    """

    affiliate_tag = _get_affiliate_tag_from_config()
    return build_affiliate_url_with_tag(product_url, affiliate_tag)


def build_affiliate_url_with_tag(product_url: str, affiliate_tag: str) -> AffiliateLinkResult:
    """Build an affiliate URL with an explicitly provided tag.

    This helper is handy for unit tests because tests can pass a known tag
    directly without depending on environment setup.
    """

    validated_url = _validate_product_url(product_url)
    validated_tag = _validate_affiliate_tag(affiliate_tag)
    affiliate_url = _append_affiliate_tag(validated_url, validated_tag)

    return AffiliateLinkResult(
        original_url=validated_url,
        affiliate_url=affiliate_url,
        affiliate_tag_used=validated_tag,
    )


def _get_affiliate_tag_from_config() -> str:
    """Read the affiliate tag through the existing config layer."""

    try:
        settings = load_settings()
    except ConfigError as error:
        raise LinkBuilderError(str(error)) from error

    return _validate_affiliate_tag(settings.amazon_associate_tag)


def _validate_affiliate_tag(affiliate_tag: str) -> str:
    """Validate the affiliate tag after it is loaded from config or tests."""

    cleaned_tag = affiliate_tag.strip()

    if not cleaned_tag:
        raise LinkBuilderError(
            "AMAZON_ASSOCIATE_TAG is missing. Add your affiliate tag to the environment before building links."
        )

    return cleaned_tag


def _validate_product_url(product_url: str) -> str:
    """Validate the input product URL before we modify it."""

    if not isinstance(product_url, str):
        raise LinkBuilderError("Product URL must be provided as a text string.")

    cleaned_url = product_url.strip()

    if not cleaned_url:
        raise LinkBuilderError("Product URL is empty. Provide a full product URL to build an affiliate link.")

    # Phase 4 allows general http/https URLs for local development.
    # A later production-hardening step may restrict URLs to expected
    # Amazon domains only.
    parsed = urlparse(cleaned_url)

    if parsed.scheme not in {"http", "https"}:
        raise LinkBuilderError("Product URL must start with http:// or https://.")

    if not parsed.netloc:
        raise LinkBuilderError("Product URL looks incomplete. Make sure it includes a valid domain name.")

    return cleaned_url


def _append_affiliate_tag(product_url: str, affiliate_tag: str) -> str:
    """Append or replace the affiliate tag query parameter safely."""

    parsed = urlparse(product_url)
    query_items = parse_qsl(parsed.query, keep_blank_values=True)

    # Remove any existing tag parameter so we do not end up with duplicates.
    filtered_items = [(key, value) for key, value in query_items if key.lower() != "tag"]
    filtered_items.append(("tag", affiliate_tag))

    updated_query = urlencode(filtered_items, doseq=True)

    # URL fragments such as "#details" are preserved automatically here
    # because we only replace the query portion of the parsed URL.
    updated_parts = parsed._replace(query=updated_query)
    return urlunparse(updated_parts)
