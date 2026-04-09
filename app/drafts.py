"""Draft generation helpers for affiliate content.

This module creates plain, helpful draft content for products without
publishing anything. It keeps the language simple and compliance-aware.
"""

from __future__ import annotations

from uuid import uuid4

from app.disclosure import build_compliance_notes, get_default_disclosure
from app.link_builder import AffiliateLinkResult, build_affiliate_url
from app.models import Product, ProductDraft


def create_deal_post(product: Product) -> ProductDraft:
    """Create a simple deal-style draft for a product."""

    affiliate_result = build_affiliate_url(product.product_url)
    disclosure_text = get_default_disclosure()

    title = f"{product.title} for {product.source_currency} {product.source_price}"
    caption = (
        f"{product.title} is available in the {product.category} category for "
        f"{product.source_currency} {product.source_price}. "
        f"It may be useful for someone comparing straightforward product options. "
        f"Link: {affiliate_result.affiliate_url}"
    )

    return _build_draft(
        product=product,
        draft_type="deal_post",
        title=title,
        caption=caption,
        affiliate_result=affiliate_result,
        disclosure_text=disclosure_text,
    )


def create_why_it_is_useful_post(product: Product) -> ProductDraft:
    """Create a plain-language 'why it is useful' draft."""

    affiliate_result = build_affiliate_url(product.product_url)
    disclosure_text = get_default_disclosure()

    title = f"Why {product.title} may be useful"
    caption = (
        f"{product.title} may be useful for people browsing {product.category} products. "
        f"It offers a simple option to review if the price and features fit your needs. "
        f"Current source price: {product.source_currency} {product.source_price}. "
        f"Link: {affiliate_result.affiliate_url}"
    )

    return _build_draft(
        product=product,
        draft_type="why_it_is_useful_post",
        title=title,
        caption=caption,
        affiliate_result=affiliate_result,
        disclosure_text=disclosure_text,
    )


def create_simple_roundup_entry(product: Product) -> ProductDraft:
    """Create a simple roundup-style entry for a product list."""

    affiliate_result = build_affiliate_url(product.product_url)
    disclosure_text = get_default_disclosure()

    title = product.title
    caption = (
        f"{product.title} is a {product.category} option listed at "
        f"{product.source_currency} {product.source_price}. "
        f"This entry is suitable for a simple roundup or comparison list. "
        f"Link: {affiliate_result.affiliate_url}"
    )

    return _build_draft(
        product=product,
        draft_type="simple_roundup_entry",
        title=title,
        caption=caption,
        affiliate_result=affiliate_result,
        disclosure_text=disclosure_text,
    )


def generate_all_draft_types(product: Product) -> list[ProductDraft]:
    """Generate all supported draft types for a single product."""

    return [
        create_deal_post(product),
        create_why_it_is_useful_post(product),
        create_simple_roundup_entry(product),
    ]


def format_publishable_text(draft: ProductDraft) -> str:
    """Combine the caption and disclosure into one final display block.

    We keep the disclosure separate in the model so it can be managed
    clearly, then combine it only when a final text block is needed.
    """

    return f"{draft.caption}\n{draft.disclosure_text}"


def _build_draft(
    product: Product,
    draft_type: str,
    title: str,
    caption: str,
    affiliate_result: AffiliateLinkResult,
    disclosure_text: str,
) -> ProductDraft:
    """Build the final structured draft object."""

    compliance_notes = build_compliance_notes()

    return ProductDraft(
        draft_id=str(uuid4()),
        product_id=product.product_id,
        draft_type=draft_type,
        title=title,
        caption=caption,
        affiliate_url=affiliate_result.affiliate_url,
        disclosure_text=disclosure_text,
        compliance_notes=compliance_notes,
    )
