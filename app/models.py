"""Simple data models used by the application."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


DRAFTED = "DRAFTED"
BLOCKED = "BLOCKED"
READY_FOR_REVIEW = "READY_FOR_REVIEW"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
PUBLISHED = "PUBLISHED"

DRAFT_STATUSES = (
    DRAFTED,
    BLOCKED,
    READY_FOR_REVIEW,
    APPROVED,
    REJECTED,
    PUBLISHED,
)


@dataclass(slots=True)
class Draft:
    """A basic draft record.

    This mirrors the structure of the `drafts` table in SQLite.
    """

    id: int | None
    title: str
    content: str
    status: str = "pending"
    created_at: datetime | None = None


@dataclass(slots=True)
class Product:
    """Structured product data returned by product source providers.

    This model lives in `models.py` because it is shared application data,
    not provider-specific logic.
    """

    product_id: str
    asin: str
    title: str
    category: str
    source_price: Decimal
    source_currency: str
    product_url: str
    image_url: str
    source_name: str
    source_timestamp_utc: str
    discount_percent: Decimal | None = None
    discount_amount: Decimal | None = None


@dataclass(slots=True)
class ProductDraft:
    """Structured draft content generated for one product."""

    draft_id: str
    product_id: str
    draft_type: str
    title: str
    caption: str
    affiliate_url: str
    disclosure_text: str
    compliance_notes: list[str]
    status: str = DRAFTED
    created_at: str | None = None
    updated_at: str | None = None
