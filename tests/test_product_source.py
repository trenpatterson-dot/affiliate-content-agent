"""Tests for the mock product source and helpers."""

from __future__ import annotations

from decimal import Decimal

from app.product_source import (
    MockProductSourceProvider,
    filter_products_by_price,
    get_all_products,
    get_products_by_category,
)


def test_mock_provider_loads_products():
    """Proves the default mock provider returns local development products."""

    products = get_all_products()

    assert len(products) >= 4
    assert products[0].product_id.startswith("mock-")


def test_get_products_by_category_filters_case_insensitively():
    """Proves category filtering works even if input casing differs."""

    products = get_products_by_category("ELECTRONICS", provider=MockProductSourceProvider())

    assert products
    assert all(product.category == "electronics" for product in products)


def test_filter_products_by_price_returns_matching_range():
    """Proves price filtering keeps only products inside the requested range."""

    products = get_all_products(provider=MockProductSourceProvider())

    filtered = filter_products_by_price(products, min_price=40, max_price=90)

    assert filtered
    assert all(Decimal("40") <= product.source_price <= Decimal("90") for product in filtered)
