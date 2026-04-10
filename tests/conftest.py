"""Shared pytest fixtures for the affiliate-content-agent test suite."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.models import Product


@pytest.fixture
def sample_product() -> Product:
    """Provide one stable product object that tests can reuse."""

    return Product(
        product_id="test-001",
        asin="B0TEST001",
        title="Test Product",
        category="electronics",
        source_price=Decimal("49.99"),
        source_currency="USD",
        product_url="https://example.com/product/test-001",
        image_url="https://example.com/image/test-001.jpg",
        source_name="test-source",
        source_timestamp_utc="2026-04-09T12:00:00+00:00",
    )
