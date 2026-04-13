"""Conversation Recall — pull full email threads from Inkbox for any contact."""

import json
from datetime import datetime


class ConversationRecall:
    def __init__(self, inkbox_identity, vault_manager):
        self.identity = inkbox_identity
        self.vault = vault_manager

    def get_conversation(self, query: str) -> dict:
        """Find a contact and return the full email conversation history."""
        # Step 1: Search vault for the contact
        contacts = self.vault.search_contacts(query)
        if not contacts:
            return {"status": "not_found", "message": f"No contacts found matching '{query}'."}

        results = []
        for contact in contacts:
            thread_ids = set()
            message_ids = []

            # Collect all thread/message IDs from outreach history
            for event in contact.get("outreach_history", []):
                tid = event.get("thread_id")
                mid = event.get("message_id")
                if tid:
                    thread_ids.add(tid)
                if mid:
                    message_ids.append(mid)

            # Step 2: Fetch full threads from Inkbox
            messages = []
            for tid in thread_ids:
                try:
                    thread = self.identity.get_thread(tid)
                    for msg in thread.messages:
                        # Messages in thread are summaries — fetch full detail for body
                        try:
                            detail = self.identity.get_message(str(msg.id))
                            body = detail.body_text or detail.body_html or ""
                        except Exception:
                            body = msg.snippet or "(body not available)"
                        messages.append({
                            "date": msg.created_at.isoformat() if msg.created_at else "",
                            "from": msg.from_address,
                            "to": msg.to_addresses,
                            "subject": msg.subject or "(no subject)",
                            "body": body,
                            "direction": str(msg.direction),
                            "is_read": msg.is_read,
                        })
                except Exception:
                    pass

            # Sort by date
            messages.sort(key=lambda m: m.get("date", ""))

            results.append({
                "contact": {
                    "name": contact["name"],
                    "email": contact["email"],
                    "company": contact.get("company", ""),
                    "warmth": contact.get("warmth_score", ""),
                    "context_notes": contact.get("context_notes", ""),
                    "venue": contact.get("venue", ""),
                    "date_met": contact.get("date_met", ""),
                },
                "messages": messages,
                "total_messages": len(messages),
            })

        return {
            "status": "found",
            "count": len(results),
            "conversations": results,
        }

    def get_all_conversations_by_venue(self, venue: str) -> dict:
        """Get conversations with everyone met at a specific event."""
        contacts = self.vault.search_by_venue(venue)
        if not contacts:
            return {"status": "not_found", "message": f"No contacts from '{venue}'."}

        results = []
        for contact in contacts:
            convo = self.get_conversation(contact["name"])
            if convo["status"] == "found":
                results.extend(convo["conversations"])

        return {
            "status": "found",
            "venue": venue,
            "count": len(results),
            "conversations": results,
        }
