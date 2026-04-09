"""Terminal review tool for the approval queue."""

from __future__ import annotations

from app.approval_queue import (
    format_draft_summary,
    get_all_drafts,
    get_compliance_result,
    get_draft_by_id,
    get_drafts_by_status,
    update_draft_status,
)
from app.config import load_settings
from app.db import initialize_database
from app.models import APPROVED, DRAFT_STATUSES, REJECTED


def main() -> int:
    """Run a simple terminal menu for reviewing queued drafts."""

    settings = load_settings()
    initialize_database(settings.database_path)

    while True:
        print()
        print("Approval Queue")
        print("1. List all drafts")
        print("2. List drafts by status")
        print("3. Inspect one draft")
        print("4. Approve a draft")
        print("5. Reject a draft")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            _list_all_drafts()
        elif choice == "2":
            _list_drafts_by_status()
        elif choice == "3":
            _inspect_draft()
        elif choice == "4":
            _change_status(APPROVED)
        elif choice == "5":
            _change_status(REJECTED)
        elif choice == "6":
            print("Goodbye.")
            return 0
        else:
            print("Please choose a valid menu option.")


def _list_all_drafts() -> None:
    drafts = get_all_drafts()

    if not drafts:
        print("No drafts found in the queue.")
        return

    print()
    for draft in drafts:
        print(format_draft_summary(draft))


def _list_drafts_by_status() -> None:
    print("Available statuses:")
    for status in DRAFT_STATUSES:
        print(f"- {status}")

    selected_status = input("Enter a status: ").strip().upper()

    try:
        drafts = get_drafts_by_status(selected_status)
    except ValueError as error:
        print(error)
        return

    if not drafts:
        print(f"No drafts found with status {selected_status}.")
        return

    print()
    for draft in drafts:
        print(format_draft_summary(draft))


def _inspect_draft() -> None:
    draft_id = input("Enter draft_id: ").strip()
    draft = get_draft_by_id(draft_id)

    if draft is None:
        print(f"Draft {draft_id} was not found.")
        return

    print()
    print(f"Draft ID: {draft.draft_id}")
    print(f"Product ID: {draft.product_id}")
    print(f"Type: {draft.draft_type}")
    print(f"Status: {draft.status}")
    print(f"Title: {draft.title}")
    print(f"Caption: {draft.caption}")
    print(f"Affiliate URL: {draft.affiliate_url}")
    print(f"Disclosure: {draft.disclosure_text}")
    print(f"Created At: {draft.created_at}")
    print(f"Updated At: {draft.updated_at}")
    print("Compliance Notes:")
    for note in draft.compliance_notes:
        print(f"- {note}")

    result = get_compliance_result(draft.draft_id)
    if result is None:
        print("Compliance Result: none saved yet")
        return

    print(f"Compliance Result: {result.status}")
    print("Checklist:")
    for key, value in result.checklist.items():
        label = "PASS" if value else "FAIL"
        print(f"- {key}: {label}")

    if result.reasons:
        print("Reasons:")
        for reason in result.reasons:
            print(f"- {reason}")
    else:
        print("Reasons: none")


def _change_status(new_status: str) -> None:
    draft_id = input("Enter draft_id: ").strip()
    draft = get_draft_by_id(draft_id)

    if draft is None:
        print(f"Draft {draft_id} was not found.")
        return

    if new_status == APPROVED:
        result = get_compliance_result(draft_id)
        if result is None:
            print("Cannot approve draft because no compliance result has been saved yet.")
            return

        if not result.passed:
            print("Cannot approve draft because compliance checks did not pass.")
            return

    try:
        updated_draft = update_draft_status(draft_id, new_status)
    except ValueError as error:
        print(error)
        return

    print(f"Draft {updated_draft.draft_id} is now {updated_draft.status}.")


if __name__ == "__main__":
    raise SystemExit(main())
