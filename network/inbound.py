"""Mode 2: Inbound — Receive emails, classify, smart reply, store, brief."""

import json
import asyncio
from datetime import date

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from config import MY_EMAIL
from models.contact import create_contact
from prompts.qualify import QUALIFY_PROMPT


def _parse_llm_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


class InboundAgent:
    def __init__(self, inkbox_identity, llm: ChatOpenAI, vault_manager):
        self.identity = inkbox_identity
        self.llm = llm
        self.vault = vault_manager

    async def check_inbox(self) -> list[dict]:
        """Poll inbox for unread emails and process each one."""
        results = []
        try:
            for msg in self.identity.iter_unread_emails():
                # Get full message detail
                detail = self.identity.get_message(str(msg.id))
                email_data = {
                    "id": str(msg.id),
                    "from": msg.from_address,
                    "to": msg.to_addresses,
                    "subject": msg.subject or "(no subject)",
                    "body": detail.body_text or detail.body_html or "",
                    "thread_id": str(msg.thread_id) if msg.thread_id else None,
                    "message_id": msg.message_id,
                    "direction": str(msg.direction),
                }

                # Skip outbound messages
                if "outbound" in str(msg.direction).lower():
                    continue

                print(f"  Processing email from {email_data['from']}: {email_data['subject']}")
                result = await self.process_email(email_data)
                results.append(result)

                # Mark as read
                self.identity.mark_emails_read([str(msg.id)])
                await asyncio.sleep(1)

        except Exception as e:
            print(f"  Error checking inbox: {e}")

        if not results:
            print("  No new inbound emails.")

        return results

    async def process_email(self, email_message: dict) -> dict:
        """Full inbound flow: classify -> reply -> store -> brief."""
        try:
            # Step 1: Classify
            result = await self._qualify(
                sender_email=email_message["from"],
                subject=email_message["subject"],
                body=email_message["body"],
            )

            print(f"    Classification: {result['classification']} | Priority: {result['priority']}")

            # Step 2: Smart reply (if needed)
            if result.get("reply_needed", False) and result["classification"] != "spam":
                print(f"    Sending reply...")
                self._send_reply(
                    to=email_message["from"],
                    subject=result.get("reply_subject", f"Re: {email_message['subject']}"),
                    body=result.get("reply_body", ""),
                    in_reply_to=email_message.get("message_id"),
                )

            # Step 3: Store in vault (if not spam)
            if result["classification"] != "spam":
                vault_entry = result.get("vault_entry", {})
                contact = create_contact(
                    name=vault_entry.get("name", "Unknown"),
                    email=email_message["from"],
                    company=vault_entry.get("company", "Unknown"),
                    source="inbound",
                    warmth_score=result.get("priority", "warm"),
                    context_notes=vault_entry.get("context_notes", email_message["subject"]),
                )
                contact["outreach_history"].append({
                    "date": date.today().isoformat(),
                    "type": "inbound",
                    "subject": email_message["subject"],
                    "thread_id": email_message.get("thread_id"),
                    "message_id": email_message.get("message_id"),
                    "reply_received": True,
                    "sentiment": None,
                })
                self.vault.store_contact(contact)

            # Step 4: Brief me (if hot or warm)
            if result.get("priority") in ["hot", "warm"]:
                self._send_briefing(email_message["from"], result)

            return result

        except Exception as e:
            print(f"    Error processing email: {e}")
            return {"classification": "error", "priority": "cold", "error": str(e)}

    async def _qualify(self, sender_email: str, subject: str, body: str) -> dict:
        """Classify and draft reply using LLM."""
        prompt = QUALIFY_PROMPT.format(
            sender_email=sender_email,
            subject=subject,
            body=body,
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return _parse_llm_json(response.content)
        except json.JSONDecodeError:
            return {
                "classification": "networking",
                "priority": "warm",
                "reply_needed": True,
                "reply_subject": f"Re: {subject}",
                "reply_body": "Thanks for reaching out! I'm Paramjeet, an AI/ML Engineer at Northeastern. I'd be happy to connect — what brings you my way?",
                "vault_entry": {"name": "Unknown", "company": "Unknown", "context_notes": subject},
                "briefing_summary": f"New email from {sender_email}: {subject}",
            }

    def _send_reply(self, to: str, subject: str, body: str, in_reply_to: str | None = None):
        """Reply, maintaining thread if possible."""
        try:
            self.identity.send_email(
                to=[to],
                subject=subject,
                body_text=body,
                in_reply_to_message_id=in_reply_to,
            )
        except Exception as e:
            print(f"    Warning: Could not send reply: {e}")

    def _send_briefing(self, sender: str, result: dict):
        """Brief me about high-value inbound contact."""
        summary = result.get("briefing_summary", f"New contact from {sender}")
        classification = result.get("classification", "unknown")
        priority = result.get("priority", "unknown")

        briefing = (
            f"New inbound contact!\n\n"
            f"From: {sender}\n"
            f"Classification: {classification}\n"
            f"Priority: {priority}\n"
            f"Summary: {summary}\n"
        )
        try:
            self.identity.send_email(
                to=[MY_EMAIL],
                subject=f"NetWork Alert: {priority.upper()} — {summary[:50]}",
                body_text=briefing,
            )
        except Exception as e:
            print(f"    Warning: Could not send briefing: {e}")
