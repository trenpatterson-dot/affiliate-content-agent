"""Product source helpers for the affiliate content agent.

This module intentionally avoids scraping Amazon product pages.
Instead, it uses a provider-based design so the data source can be
swapped later with minimal code changes.

For Phase 2, we include:
- a shared product data structure
- a provider interface
- a mock provider for local development and testing
- helper functions to fetch and filter products

The long-term goal is simple:
- today: use a mock provider locally
- later: replace a legacy PA-API provider with a Creators API provider
- keep the rest of the app mostly unchanged
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from app.models import Product


class ProductSourceProvider(ABC):
    """Base class for all product providers.

    Any future provider should implement the same method so the calling
    code does not need to care whether data came from a mock source,
    a legacy PA-API integration, or a future Creators API integration.
    """

    @abstractmethod
    def get_products_by_category(self, category: str) -> list[Product]:
        """Return products for a category."""

    def get_all_products(self) -> list[Product]:
        """Return every available product.

        This default method keeps the interface friendly for simple use cases.
        Providers can override it with a more efficient implementation later.
        """

        raise NotImplementedError("This provider does not support get_all_products().")


class MockProductSourceProvider(ProductSourceProvider):
    """Simple in-memory provider used for local development.

    This gives us predictable sample data without hitting any external
    service, which makes local testing much easier.
    """

    def __init__(self) -> None:
        timestamp = datetime.now(UTC).isoformat()

        self._products: list[Product] = [
            Product(
                product_id="mock-001",
                asin="B0MOCK001",
                title="Compact Mechanical Keyboard",
                category="electronics",
                source_price=Decimal("79.99"),
                source_currency="USD",
                # example.com URLs are placeholders for local development only.
                product_url="https://example.com/products/mock-001",
                image_url="https://example.com/images/mock-001.jpg",
                source_name="mock-provider",
                source_timestamp_utc=timestamp,
            ),
            Product(
                product_id="mock-002",
                asin="B0MOCK002",
                title="USB-C Docking Station",
                category="electronics",
                source_price=Decimal("129.00"),
                source_currency="USD",
                product_url="https://example.com/products/mock-002",
                image_url="https://example.com/images/mock-002.jpg",
                source_name="mock-provider",
                source_timestamp_utc=timestamp,
            ),
            Product(
                product_id="mock-003",
                asin="B0MOCK003",
                title="Ergonomic Office Chair Cushion",
                category="office",
                source_price=Decimal("34.50"),
                source_currency="USD",
                product_url="https://example.com/products/mock-003",
                image_url="https://example.com/images/mock-003.jpg",
                source_name="mock-provider",
                source_timestamp_utc=timestamp,
            ),
            Product(
                product_id="mock-004",
                asin="B0MOCK004",
                title="Glass Meal Prep Container Set",
                category="kitchen",
                source_price=Decimal("42.00"),
                source_currency="USD",
                product_url="https://example.com/products/mock-004",
                image_url="https://example.com/images/mock-004.jpg",
                source_name="mock-provider",
                source_timestamp_utc=timestamp,
            ),
        ]

    def get_products_by_category(self, category: str) -> list[Product]:
        """Return all products whose category matches the requested value."""
        normalized_category = category.strip().lower()

        return [
            product
            for product in self._products
            if product.category.strip().lower() == normalized_category
        ]

    def get_all_products(self) -> list[Product]:
        """Return every mock product."""

        return list(self._products)


def get_default_provider() -> ProductSourceProvider:
    """Return the provider used by default in Phase 2.

    For now this is the mock provider. Later, this function is the main
    place where we can swap in a real API-backed provider.
    """

    return MockProductSourceProvider()


def get_products_by_category(
    category: str,
    provider: ProductSourceProvider | None = None,
) -> list[Product]:
    """Fetch products for a category using the selected provider.

    Passing a provider explicitly makes this easy to test because tests
    can supply a fake provider without changing the function itself.
    """

    active_provider = provider or get_default_provider()
    return active_provider.get_products_by_category(category)


def get_all_products(provider: ProductSourceProvider | None = None) -> list[Product]:
    """Return every product from the selected provider."""

    active_provider = provider or get_default_provider()
    return active_provider.get_all_products()


def filter_products_by_price(
    products: list[Product],
    min_price: Decimal | float | int | str | None = None,
    max_price: Decimal | float | int | str | None = None,
) -> list[Product]:
    """Filter products by a minimum and/or maximum price.

    If a boundary is not provided, that side is left open.
    Example:
    - min_price=25 means price must be 25 or more
    - max_price=100 means price must be 100 or less
    """

    minimum = _to_decimal(min_price) if min_price is not None else None
    maximum = _to_decimal(max_price) if max_price is not None else None

    filtered_products: list[Product] = []

    for product in products:
        if minimum is not None and product.source_price < minimum:
            continue

        if maximum is not None and product.source_price > maximum:
            continue

        filtered_products.append(product)

    return filtered_products


def _to_decimal(value: Decimal | float | int | str) -> Decimal:
    """Convert common numeric input types into Decimal safely."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid price value: {value!r}") from error
