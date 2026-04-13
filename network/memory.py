"""Vault-backed CRM storage using Inkbox vault with OtherPayload for JSON contacts."""

import json
from datetime import date
from inkbox.vault.types import OtherPayload


class VaultManager:
    def __init__(self, inkbox_client, vault_key: str):
        self.inkbox = inkbox_client
        self.vault_key = vault_key
        self._unlocked = None
        self._ensure_vault()

    def _ensure_vault(self):
        """Initialize vault if needed, then unlock."""
        info = self.inkbox.vault.info()
        if info is None:
            self.inkbox.vault.initialize(self.vault_key)
        self._unlocked = self.inkbox.vault.unlock(self.vault_key)

    def _contact_key(self, email: str) -> str:
        return f"contact:{email.lower().strip()}"

    def _find_secret_by_name(self, name: str):
        """Find a secret by its name. Returns DecryptedVaultSecret or None."""
        for secret in self._unlocked.secrets:
            if secret.name == name:
                return secret
        return None

    def store_contact(self, contact: dict) -> str:
        """Store contact in vault. Updates if exists, creates if not."""
        key = self._contact_key(contact["email"])
        existing = self._find_secret_by_name(key)

        payload = OtherPayload(data=json.dumps(contact))

        if existing:
            self._unlocked.update_secret(
                str(existing.id),
                payload=payload,
            )
            return key

        self._unlocked.create_secret(
            name=key,
            payload=payload,
            description=f"Contact: {contact['name']} ({contact.get('company', 'Unknown')})",
        )
        return key

    def get_contact(self, email: str) -> dict | None:
        """Retrieve contact by email."""
        key = self._contact_key(email)
        secret = self._find_secret_by_name(key)
        if secret is None:
            return None
        return json.loads(secret.payload.data)

    def update_contact(self, email: str, updates: dict) -> bool:
        """Partial update of contact fields."""
        contact = self.get_contact(email)
        if contact is None:
            return False
        contact.update(updates)
        contact["updated_at"] = date.today().isoformat()
        self.store_contact(contact)
        return True

    def search_by_venue(self, venue: str) -> list[dict]:
        """Find all contacts from a specific venue/event."""
        results = []
        for contact in self.get_all_contacts():
            if venue.lower() in contact.get("venue", "").lower():
                results.append(contact)
        return results

    def search_by_time(self, days_ago: int) -> list[dict]:
        """Find contacts not contacted in X days."""
        results = []
        for contact in self.get_all_contacts():
            history = contact.get("outreach_history", [])
            if not history:
                results.append(contact)
                continue
            last_date_str = history[-1].get("date", "")
            try:
                last = date.fromisoformat(last_date_str)
                if (date.today() - last).days >= days_ago:
                    results.append(contact)
            except (ValueError, TypeError):
                results.append(contact)
        return results

    def get_stale_contacts(self) -> list[dict]:
        """Get contacts that need follow-up."""
        results = []
        for contact in self.get_all_contacts():
            if contact["follow_up_count"] >= contact["max_follow_ups"]:
                continue
            nfu = contact.get("next_follow_up")
            if not nfu:
                continue
            try:
                if date.fromisoformat(nfu) <= date.today():
                    results.append(contact)
            except (ValueError, TypeError):
                continue
        return results

    def get_all_contacts(self) -> list[dict]:
        """Return all contacts from vault."""
        contacts = []
        for secret in self._unlocked.secrets:
            if secret.name.startswith("contact:"):
                try:
                    contacts.append(json.loads(secret.payload.data))
                except (json.JSONDecodeError, AttributeError):
                    continue
        return contacts

    def add_outreach_event(self, email: str, event: dict):
        """Append to contact's outreach_history."""
        contact = self.get_contact(email)
        if contact is None:
            return
        contact["outreach_history"].append(event)
        contact["updated_at"] = date.today().isoformat()
        self.store_contact(contact)

    def update_warmth(self, email: str, warmth: str):
        """Update warmth score after sentiment analysis."""
        self.update_contact(email, {"warmth_score": warmth})

    def search_contacts(self, query: str) -> list[dict]:
        """Full-text search across contact fields."""
        query_lower = query.lower()
        results = []
        for contact in self.get_all_contacts():
            searchable = json.dumps(contact).lower()
            if query_lower in searchable:
                results.append(contact)
        return results
