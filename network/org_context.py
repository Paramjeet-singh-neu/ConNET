"""Org-wide Inkbox Contacts + Notes context for inbound handling."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from inkbox import Inkbox
from inkbox.contacts.types import Contact
from inkbox.notes.types import Note

logger = logging.getLogger(__name__)


def _domain_from_email(email: str) -> str | None:
    email = (email or "").strip().lower()
    if "@" not in email:
        return None
    dom = email.rsplit("@", 1)[-1].strip()
    return dom or None


def _contact_lines(contact: Contact, index: int) -> str:
    name_bits = [
        contact.preferred_name,
        " ".join(
            p
            for p in (
                contact.given_name or "",
                contact.family_name or "",
            )
            if p
        ).strip()
        or None,
    ]
    display_name = next((n for n in name_bits if n), "Unknown")
    lines = [
        f"  Match {index + 1}: {display_name}",
        f"    company: {contact.company_name or '-'}",
        f"    job_title: {contact.job_title or '-'}",
    ]
    if contact.notes:
        note_preview = contact.notes.replace("\n", " ")[:240]
        lines.append(f"    contact_card_notes: {note_preview}")
    if contact.emails:
        lines.append(
            "    emails: "
            + ", ".join(f"{e.value} ({e.label or 'n/a'})" for e in contact.emails[:5])
        )
    if contact.phones:
        lines.append(
            "    phones: "
            + ", ".join(f"{p.value} ({p.label or 'n/a'})" for p in contact.phones[:5])
        )
    return "\n".join(lines)


def _format_contacts_block(contacts: list[Contact]) -> str:
    if not contacts:
        return "(none)"
    trimmed = contacts[:5]
    parts = [_contact_lines(c, i) for i, c in enumerate(trimmed)]
    if len(contacts) > len(trimmed):
        parts.append(f"  …and {len(contacts) - len(trimmed)} more matches not shown.")
    return "\n".join(parts)


def _format_note_snippets(notes: list[Note]) -> str:
    if not notes:
        return "(none)"
    parts: list[str] = []
    for n in notes[:8]:
        title = n.title or "(no title)"
        body = (n.body or "").replace("\n", " ")[:400]
        parts.append(f"  - [{title}] {body}")
    return "\n".join(parts)


def _gather_sync(inkbox: Inkbox, identity_id: Any, sender_email: str) -> tuple[str, str]:
    """Blocking: reverse-lookup contacts + list notes. Returns (contacts_block, notes_block)."""
    contacts: list[Contact] = []
    sender_email = (sender_email or "").strip()
    try:
        if sender_email:
            contacts = inkbox.contacts.lookup(email=sender_email)
    except Exception as e:
        logger.warning("contacts.lookup(email=…) failed: %s", e)

    domain = _domain_from_email(sender_email)
    if not contacts and domain:
        try:
            contacts = inkbox.contacts.lookup(email_domain=domain)
        except Exception as e:
            logger.warning("contacts.lookup(email_domain=…) failed: %s", e)

    contacts_block = _format_contacts_block(contacts)

    seen: set[str] = set()
    merged_notes: list[Note] = []
    queries: list[str] = []
    if sender_email:
        queries.append(sender_email[:200])
    if domain and domain not in queries and len(domain) > 2:
        queries.append(domain[:200])

    for q in queries:
        if not q.strip():
            continue
        try:
            batch = inkbox.notes.list(
                q=q.strip(),
                identity_id=identity_id,
                limit=6,
                order="recent",
            )
        except Exception as e:
            logger.warning("notes.list(q=…) failed for %r: %s", q[:40], e)
            continue
        for note in batch:
            sid = str(note.id)
            if sid not in seen:
                seen.add(sid)
                merged_notes.append(note)

    merged_notes.sort(key=lambda n: n.updated_at, reverse=True)
    notes_block = _format_note_snippets(merged_notes)
    return contacts_block, notes_block


async def gather_inbound_org_context(
    inkbox: Inkbox | None,
    identity_id: Any,
    sender_email: str,
    enabled: bool,
) -> tuple[str, str]:
    """Return (org_contacts_text, org_notes_text) for qualify prompt."""
    if not enabled or inkbox is None:
        return "(none)", "(none)"
    return await asyncio.to_thread(_gather_sync, inkbox, identity_id, sender_email)


def lookup_phone_contacts(inkbox: Inkbox | None, e164: str) -> list[Contact]:
    """Sync helper for SMS / tooling; returns [] on failure."""
    if inkbox is None or not e164:
        return []
    try:
        return inkbox.contacts.lookup(phone=e164.strip())
    except Exception as e:
        logger.warning("contacts.lookup(phone=…) failed: %s", e)
        return []
