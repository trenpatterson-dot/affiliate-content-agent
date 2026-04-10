"""Tests for product scoring helpers."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from app.deal_scoring import score_product, score_products, sort_scored_products


def test_score_product_returns_score_and_reasons(sample_product):
    """Proves scoring returns a bounded score plus human-readable reasons."""

    result = score_product(sample_product, target_category="electronics", min_price=25, max_price=100)

    assert 1 <= result.score <= 100
    assert result.product.product_id == sample_product.product_id
    assert result.reasons


def test_score_product_uses_discount_metadata_when_present(sample_product):
    """Proves optional discount fields can improve the scoring output."""

    discounted = replace(sample_product, discount_percent=Decimal("25"))

    result = score_product(discounted, target_category="electronics")

    assert any("discount" in reason.lower() for reason in result.reasons)


def test_sort_scored_products_orders_highest_first(sample_product):
    """Proves scored products can be ranked from highest score to lowest."""

    lower_fit = replace(
        sample_product,
        product_id="test-002",
        category="office",
        source_price=Decimal("300.00"),
    )

    scored = score_products(
        [lower_fit, sample_product],
        target_category="electronics",
        min_price=25,
        max_price=100,
    )
    ordered = sort_scored_products(scored)

    assert ordered[0].score >= ordered[1].score
