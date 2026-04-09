"""Facebook Page publisher for approved drafts.

Phase 8 keeps publishing safe by default:
- drafts must already be APPROVED
- DRY_RUN mode prints what would happen
- live publishing is intentionally not implemented yet

This module is designed so other publishers can follow a similar shape later.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import ConfigError, load_settings, mask_secret
from app.drafts import format_publishable_text
from app.logger import setup_logger
from app.models import APPROVED, ProductDraft


class PublisherError(Exception):
    """Raised when a draft cannot be published safely."""


@dataclass(slots=True)
class PublishResult:
    """Structured result for a publish attempt."""

    draft_id: str
    attempted: bool
    published: bool
    dry_run: bool
    platform: str
    message: str


def publish_to_facebook_page(draft: ProductDraft) -> PublishResult:
    """Publish or simulate publishing one approved draft to a Facebook Page."""

    settings = _load_publisher_settings()
    logger = setup_logger(settings.log_level)

    if draft.status != APPROVED:
        message = (
            f"Draft {draft.draft_id} cannot be published because its status is "
            f"{draft.status}, not {APPROVED}."
        )
        logger.error(message)
        return PublishResult(
            draft_id=draft.draft_id,
            attempted=False,
            published=False,
            dry_run=settings.dry_run,
            platform="facebook_page",
            message=message,
        )

    publishable_text = _build_publishable_text(draft)

    if settings.dry_run:
        message = _build_dry_run_message(
            draft=draft,
            page_id=settings.facebook_page_id,
            publishable_text=publishable_text,
        )
        logger.info("DRY_RUN publish for Facebook Page draft %s", draft.draft_id)
        print(message)
        return PublishResult(
            draft_id=draft.draft_id,
            attempted=True,
            published=False,
            dry_run=True,
            platform="facebook_page",
            message="DRY_RUN completed. No live publish request was made.",
        )

    if not settings.facebook_page_id:
        message = "FACEBOOK_PAGE_ID is required for live Facebook Page publishing."
        logger.error(message)
        raise PublisherError(message)

    if not settings.facebook_page_access_token:
        message = "FACEBOOK_PAGE_ACCESS_TOKEN is required for live Facebook Page publishing."
        logger.error(message)
        raise PublisherError(message)

    logger.info("Live Facebook Page publish requested for draft %s", draft.draft_id)
    raise NotImplementedError(
        "Live Facebook Page publishing is not implemented yet. Set DRY_RUN=true to preview output safely."
    )


def _load_publisher_settings():
    """Load settings through the shared config layer."""

    try:
        return load_settings()
    except ConfigError as error:
        raise PublisherError(str(error)) from error


def _build_publishable_text(draft: ProductDraft) -> str:
    """Return the text body that would be published."""

    return format_publishable_text(draft)


def _build_dry_run_message(
    draft: ProductDraft,
    page_id: str | None,
    publishable_text: str,
) -> str:
    """Format readable terminal output for a DRY_RUN publish attempt."""

    safe_page_id = mask_secret(page_id)

    return (
        "DRY RUN: Facebook Page publish preview\n"
        f"Draft ID: {draft.draft_id}\n"
        f"Platform: facebook_page\n"
        f"Target Page ID: {safe_page_id}\n"
        "Post Body:\n"
        f"{publishable_text}"
    )
