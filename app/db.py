"""Database helpers for SQLite."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.models import ProductDraft


def _ensure_data_directory(database_path: Path) -> None:
    """Create the parent folder for the SQLite database if needed."""
    database_path.parent.mkdir(parents=True, exist_ok=True)


def get_connection(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with row access by column name."""
    _ensure_data_directory(database_path)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: Path) -> None:
    """Create the database file and required active tables."""
    connection = get_connection(database_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS product_drafts (
                draft_id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                draft_type TEXT NOT NULL,
                title TEXT NOT NULL,
                caption TEXT NOT NULL,
                affiliate_url TEXT NOT NULL,
                disclosure_text TEXT NOT NULL,
                compliance_notes TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_results (
                draft_id TEXT PRIMARY KEY,
                passed INTEGER NOT NULL,
                reasons TEXT NOT NULL,
                checklist TEXT NOT NULL,
                reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (draft_id) REFERENCES product_drafts (draft_id)
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def row_to_product_draft(row: sqlite3.Row) -> ProductDraft:
    """Convert a SQLite row into a ProductDraft model."""

    compliance_notes = json.loads(row["compliance_notes"]) if row["compliance_notes"] else []

    return ProductDraft(
        draft_id=row["draft_id"],
        product_id=row["product_id"],
        draft_type=row["draft_type"],
        title=row["title"],
        caption=row["caption"],
        affiliate_url=row["affiliate_url"],
        disclosure_text=row["disclosure_text"],
        compliance_notes=compliance_notes,
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
