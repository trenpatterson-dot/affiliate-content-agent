"""Simple deal scoring helpers for affiliate product evaluation.

This module keeps scoring logic:
- readable
- beginner-friendly
- easy to test

It does not scrape anything and it avoids risky marketing claims.
The score is meant to help rank products internally, not to make
public claims about popularity or sales performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from app.models import Product


@dataclass(slots=True)
class ScoringResult:
    """The result of scoring one product."""

    product: Product
    score: int
    reasons: list[str]


def score_product(
    product: Product,
    target_category: str | None = None,
    min_price: Decimal | float | int | str | None = None,
    max_price: Decimal | float | int | str | None = None,
) -> ScoringResult:
    """Score one product on a simple 1 to 100 scale.

    Scoring areas:
    - niche/category fit
    - price range fit
    - optional discount metadata
    - optional freshness
    """

    score = 0
    reasons: list[str] = []

    score += _score_category_fit(product, target_category, reasons)
    score += _score_price_fit(product, min_price, max_price, reasons)
    score += _score_discount(product, reasons)
    score += _score_freshness(product, reasons)

    final_score = max(1, min(100, score))
    return ScoringResult(product=product, score=final_score, reasons=reasons)


def score_products(
    products: list[Product],
    target_category: str | None = None,
    min_price: Decimal | float | int | str | None = None,
    max_price: Decimal | float | int | str | None = None,
) -> list[ScoringResult]:
    """Score a list of products using the same scoring inputs."""

    return [
        score_product(
            product=product,
            target_category=target_category,
            min_price=min_price,
            max_price=max_price,
        )
        for product in products
    ]


def sort_scored_products(scored_products: list[ScoringResult]) -> list[ScoringResult]:
    """Return scored products from highest score to lowest."""

    return sorted(scored_products, key=lambda item: item.score, reverse=True)


def _score_category_fit(
    product: Product,
    target_category: str | None,
    reasons: list[str],
) -> int:
    """Score how well the product matches the requested category."""

    if not target_category:
        reasons.append("No target category was provided, so category fit used a neutral score.")
        return 20

    if product.category.strip().lower() == target_category.strip().lower():
        reasons.append("Category is a strong match for the requested niche.")
        return 35

    reasons.append("Category is outside the requested niche, so fit is lower.")
    return 10


def _score_price_fit(
    product: Product,
    min_price: Decimal | float | int | str | None,
    max_price: Decimal | float | int | str | None,
    reasons: list[str],
) -> int:
    """Score how well the product fits the target price range."""

    minimum = _to_decimal(min_price) if min_price is not None else None
    maximum = _to_decimal(max_price) if max_price is not None else None
    price = product.source_price

    if minimum is None and maximum is None:
        reasons.append("No target price range was provided, so price fit used a neutral score.")
        return 20

    if minimum is not None and price < minimum:
        reasons.append("Price is below the preferred range.")
        return 12

    if maximum is not None and price > maximum:
        reasons.append("Price is above the preferred range.")
        return 12

    reasons.append("Price fits within the preferred range.")
    return 35


def _score_discount(product: Product, reasons: list[str]) -> int:
    """Score optional discount information when it exists.

    The product model does not require discount fields, so we check
    for optional attributes safely with `getattr`.
    """

    discount_percent = getattr(product, "discount_percent", None)
    discount_amount = getattr(product, "discount_amount", None)

    if discount_percent is None and discount_amount is None:
        reasons.append("No discount metadata was available.")
        return 5

    if discount_percent is not None:
        percent = _to_decimal(discount_percent)

        if percent >= Decimal("20"):
            reasons.append("Discount metadata shows a strong percentage discount.")
            return 15

        if percent > Decimal("0"):
            reasons.append("Discount metadata shows a modest percentage discount.")
            return 10

    if discount_amount is not None:
        amount = _to_decimal(discount_amount)

        if amount > Decimal("0"):
            reasons.append("Discount metadata shows a direct price reduction.")
            return 10

    reasons.append("Discount metadata was present but did not improve the score.")
    return 5


def _score_freshness(product: Product, reasons: list[str]) -> int:
    """Score recent source timestamps when available."""

    timestamp_text = getattr(product, "source_timestamp_utc", None)

    if not timestamp_text:
        reasons.append("No source timestamp was available for freshness scoring.")
        return 5

    parsed_timestamp = _parse_timestamp(timestamp_text)

    if parsed_timestamp is None:
        reasons.append("Source timestamp could not be parsed, so freshness used a low score.")
        return 5

    age = datetime.now(UTC) - parsed_timestamp

    if age.days <= 1:
        reasons.append("Product data is very recent.")
        return 15

    if age.days <= 7:
        reasons.append("Product data is recent.")
        return 10

    if age.days <= 30:
        reasons.append("Product data is somewhat recent.")
        return 7

    reasons.append("Product data is older, so freshness is lower.")
    return 3


def _parse_timestamp(value: str) -> datetime | None:
    """Parse an ISO-style timestamp into a timezone-aware datetime."""

    normalized = value.strip()

    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC)


def _to_decimal(value: Decimal | float | int | str) -> Decimal:
    """Convert common numeric input types into Decimal safely."""

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid numeric value: {value!r}") from error
