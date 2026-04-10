"""Tests for draft queue persistence and status changes."""

from __future__ import annotations

import pytest

from app.approval_queue import (
    get_compliance_result,
    get_draft_by_id,
    get_drafts_by_status,
    save_compliance_result,
    save_draft,
    update_draft_status,
)
from app.compliance import ComplianceResult
from app.disclosure import get_default_disclosure
from app.models import APPROVED, DRAFTED, PUBLISHED, READY_FOR_REVIEW, ProductDraft


def _make_queue_draft() -> ProductDraft:
    """Build one stable draft for queue tests."""

    return ProductDraft(
        draft_id="queue-draft-001",
        product_id="product-001",
        draft_type="deal_post",
        title="Queue Test Draft",
        caption="Queue test caption",
        affiliate_url="https://example.com/item?tag=yourtag-20",
        disclosure_text=get_default_disclosure(),
        compliance_notes=["Review before publishing."],
        status=DRAFTED,
    )


def test_save_and_load_draft_round_trip(tmp_path):
    """Proves a saved draft can be loaded back from SQLite."""

    database_path = tmp_path / "queue.db"
    saved = save_draft(_make_queue_draft(), database_path)
    loaded = get_draft_by_id(saved.draft_id, database_path)

    assert loaded is not None
    assert loaded.draft_id == saved.draft_id
    assert loaded.status == DRAFTED


def test_update_draft_status_and_filter_by_status(tmp_path):
    """Proves draft statuses can be updated and queried cleanly."""

    database_path = tmp_path / "queue.db"
    saved = save_draft(_make_queue_draft(), database_path)
    updated = update_draft_status(saved.draft_id, READY_FOR_REVIEW, database_path)
    filtered = get_drafts_by_status(READY_FOR_REVIEW, database_path)

    assert updated.status == READY_FOR_REVIEW
    assert any(draft.draft_id == saved.draft_id for draft in filtered)


def test_save_and_load_compliance_result(tmp_path):
    """Proves compliance results are stored alongside the draft queue."""

    database_path = tmp_path / "queue.db"
    save_draft(_make_queue_draft(), database_path)

    result = ComplianceResult(
        draft_id="queue-draft-001",
        passed=True,
        reasons=[],
        checklist={"disclosure_present": True},
    )

    save_compliance_result(result, database_path)
    loaded = get_compliance_result("queue-draft-001", database_path)

    assert loaded is not None
    assert loaded.passed is True
    assert loaded.checklist["disclosure_present"] is True


def test_published_status_requires_prior_approval(tmp_path):
    """Proves queue rules block direct publishing before approval."""

    database_path = tmp_path / "queue.db"
    saved = save_draft(_make_queue_draft(), database_path)

    with pytest.raises(ValueError) as error:
        update_draft_status(saved.draft_id, PUBLISHED, database_path)

    assert "only move to PUBLISHED after they are APPROVED" in str(error.value)


def test_published_status_is_allowed_after_approval(tmp_path):
    """Proves publishing becomes allowed once a draft is already approved."""

    database_path = tmp_path / "queue.db"
    saved = save_draft(_make_queue_draft(), database_path)
    update_draft_status(saved.draft_id, APPROVED, database_path)
    updated = update_draft_status(saved.draft_id, PUBLISHED, database_path)

    assert updated.status == PUBLISHED
