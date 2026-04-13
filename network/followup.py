"""Auto follow-up engine — checks vault for stale contacts, drafts and sends follow-ups."""

import json
import asyncio
from datetime import date

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from models.contact import calculate_next_followup, days_since_last_contact
from prompts.research import RESEARCH_PROMPT
from prompts.followup_draft import FOLLOWUP_PROMPT
from live_feed import feed


def _parse_llm_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


class FollowUpEngine:
    def __init__(self, inkbox_identity, llm: ChatOpenAI, vault_manager):
        self.identity = inkbox_identity
        self.llm = llm
        self.vault = vault_manager

    async def run_follow_ups(self) -> list[dict]:
        """Check vault for stale contacts, send follow-ups."""
        stale = self.vault.get_stale_contacts()
        if not stale:
            print("  No contacts need follow-up right now.")
            return []

        print(f"  Found {len(stale)} contacts needing follow-up.")
        results = []

        for contact in stale:
            result = await self._follow_up(contact)
            results.append(result)
            await asyncio.sleep(1)

        return results

    async def _follow_up(self, contact: dict) -> dict:
        """Research fresh angle, draft and send follow-up."""
        name = contact["name"]
        company = contact["company"]
        print(f"  Following up with {name} at {company}...")

        try:
            # Step 1: Get fresh research
            fresh = await self._fresh_research(name, company)

            # Step 2: Draft follow-up
            history = contact.get("outreach_history", [])
            last_outreach = history[-1] if history else {}
            days = days_since_last_contact(contact)

            email = await self._draft_followup(
                contact=contact,
                original_email=last_outreach,
                warmth=contact.get("warmth_score", "warm"),
                fresh_research=fresh,
                days_elapsed=days,
            )

            # Step 3: Send as reply in same thread
            in_reply_to = last_outreach.get("message_id")
            msg = self.identity.send_email(
                to=[contact["email"]],
                subject=email["subject"],
                body_text=email["body"],
                in_reply_to_message_id=in_reply_to,
            )

            # Step 4: Update vault
            contact["follow_up_count"] += 1
            contact["outreach_history"].append({
                "date": date.today().isoformat(),
                "type": "follow_up",
                "subject": email["subject"],
                "thread_id": str(msg.thread_id) if msg.thread_id else last_outreach.get("thread_id"),
                "message_id": msg.message_id,
                "reply_received": False,
                "sentiment": None,
            })
            # Set next follow-up based on warmth
            wait = {"hot": 3, "warm": 7, "cold": 14}.get(contact.get("warmth_score", "warm"), 7)
            contact["next_follow_up"] = calculate_next_followup(wait)
            self.vault.store_contact(contact)

            feed.log_followup(name, contact["follow_up_count"], email["subject"])

            print(f"    Sent follow-up #{contact['follow_up_count']} to {name}")
            return {"status": "sent", "contact": name, "email": email}

        except Exception as e:
            print(f"    Error following up with {name}: {e}")
            return {"status": "error", "contact": name, "error": str(e)}

    async def _fresh_research(self, name: str, company: str) -> str:
        """Quick research for fresh angles."""
        prompt = RESEARCH_PROMPT.format(name=name, company=company)
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content

    async def _draft_followup(self, contact: dict, original_email: dict, warmth: str, fresh_research: str, days_elapsed: int) -> dict:
        """Draft follow-up email."""
        prompt = FOLLOWUP_PROMPT.format(
            contact_json=json.dumps({k: contact[k] for k in ["name", "company", "role", "context_notes", "warmth_score"]}, indent=2),
            original_email=json.dumps(original_email, indent=2),
            days_elapsed=days_elapsed,
            attempt_number=contact["follow_up_count"] + 1,
            warmth=warmth,
            fresh_research=fresh_research,
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return _parse_llm_json(response.content)
        except json.JSONDecodeError:
            return {
                "subject": f"Re: {original_email.get('subject', 'Following up')}",
                "body": f"Hi {contact['name']}, just wanted to follow up on my earlier note. Would love to connect if the timing works!",
                "fresh_angle": "generic follow-up",
            }
