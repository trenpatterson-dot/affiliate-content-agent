"""SQLite-backed approval queue helpers for human review.

This module stores generated drafts and compliance results in SQLite,
then provides simple helper functions for review and status updates.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.compliance import ComplianceResult
from app.config import load_settings
from app.db import get_connection, initialize_database, row_to_product_draft
from app.models import APPROVED, DRAFT_STATUSES, PUBLISHED, ProductDraft


def save_draft(draft: ProductDraft, database_path: Path | None = None) -> ProductDraft:
    """Insert or replace a product draft in SQLite."""

    db_path = _resolve_database_path(database_path)
    initialize_database(db_path)

    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO product_drafts (
                draft_id,
                product_id,
                draft_type,
                title,
                caption,
                affiliate_url,
                disclosure_text,
                compliance_notes,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                draft.draft_id,
                draft.product_id,
                draft.draft_type,
                draft.title,
                draft.caption,
                draft.affiliate_url,
                draft.disclosure_text,
                json.dumps(draft.compliance_notes),
                draft.status,
            ),
        )
        connection.commit()
    finally:
        connection.close()

    saved_draft = get_draft_by_id(draft.draft_id, db_path)
    if saved_draft is None:
        raise ValueError(f"Draft {draft.draft_id} could not be reloaded after saving.")
    return saved_draft


def update_draft_status(
    draft_id: str,
    new_status: str,
    database_path: Path | None = None,
) -> ProductDraft:
    """Update the status for one draft with a simple safety guard."""

    if new_status not in DRAFT_STATUSES:
        raise ValueError(f"Unsupported draft status: {new_status}")

    existing_draft = get_draft_by_id(draft_id, database_path)
    if existing_draft is None:
        raise ValueError(f"Draft {draft_id} was not found.")

    if new_status == PUBLISHED and existing_draft.status != APPROVED:
        raise ValueError("Drafts can only move to PUBLISHED after they are APPROVED.")

    db_path = _resolve_database_path(database_path)
    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE product_drafts
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE draft_id = ?
            """,
            (new_status, draft_id),
        )
        connection.commit()
    finally:
        connection.close()

    updated_draft = get_draft_by_id(draft_id, db_path)
    if updated_draft is None:
        raise ValueError(f"Draft {draft_id} could not be reloaded after update.")
    return updated_draft


def get_drafts_by_status(
    status: str,
    database_path: Path | None = None,
) -> list[ProductDraft]:
    """Return drafts for one status, newest first."""

    if status not in DRAFT_STATUSES:
        raise ValueError(f"Unsupported draft status: {status}")

    db_path = _resolve_database_path(database_path)
    initialize_database(db_path)

    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM product_drafts
            WHERE status = ?
            ORDER BY created_at DESC, draft_id ASC
            """,
            (status,),
        )
        rows = cursor.fetchall()
    finally:
        connection.close()

    return [row_to_product_draft(row) for row in rows]


def get_all_drafts(database_path: Path | None = None) -> list[ProductDraft]:
    """Return all drafts in the queue, newest first."""

    db_path = _resolve_database_path(database_path)
    initialize_database(db_path)

    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM product_drafts
            ORDER BY created_at DESC, draft_id ASC
            """
        )
        rows = cursor.fetchall()
    finally:
        connection.close()

    return [row_to_product_draft(row) for row in rows]


def get_draft_by_id(
    draft_id: str,
    database_path: Path | None = None,
) -> ProductDraft | None:
    """Return one draft by id or None if it does not exist."""

    db_path = _resolve_database_path(database_path)
    initialize_database(db_path)

    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM product_drafts
            WHERE draft_id = ?
            """,
            (draft_id,),
        )
        row = cursor.fetchone()
    finally:
        connection.close()

    if row is None:
        return None

    return row_to_product_draft(row)


def save_compliance_result(
    result: ComplianceResult,
    database_path: Path | None = None,
) -> ComplianceResult:
    """Insert or replace a compliance result for a draft."""

    db_path = _resolve_database_path(database_path)
    initialize_database(db_path)

    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO compliance_results (
                draft_id,
                passed,
                reasons,
                checklist
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                result.draft_id,
                1 if result.passed else 0,
                json.dumps(result.reasons),
                json.dumps(result.checklist),
            ),
        )
        connection.commit()
    finally:
        connection.close()

    saved_result = get_compliance_result(result.draft_id, db_path)
    if saved_result is None:
        raise ValueError(f"Compliance result for {result.draft_id} could not be reloaded after saving.")
    return saved_result


def get_compliance_result(
    draft_id: str,
    database_path: Path | None = None,
) -> ComplianceResult | None:
    """Return the saved compliance result for a draft if it exists."""

    db_path = _resolve_database_path(database_path)
    initialize_database(db_path)

    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM compliance_results
            WHERE draft_id = ?
            """,
            (draft_id,),
        )
        row = cursor.fetchone()
    finally:
        connection.close()

    if row is None:
        return None

    return ComplianceResult(
        draft_id=row["draft_id"],
        passed=bool(row["passed"]),
        reasons=json.loads(row["reasons"]) if row["reasons"] else [],
        checklist=json.loads(row["checklist"]) if row["checklist"] else {},
    )


def format_draft_summary(draft: ProductDraft) -> str:
    """Return a compact summary string for terminal review."""

    return (
        f"[{draft.status}] {draft.draft_id} | {draft.draft_type} | "
        f"{draft.title} | product={draft.product_id}"
    )


def _resolve_database_path(database_path: Path | None = None) -> Path:
    """Return the active database path.

    Centralizing this here keeps queue helpers easy to call from scripts.
    """

    if database_path is not None:
        return database_path

    return load_settings().database_path
