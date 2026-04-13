"""Mode 1: Outbound — Research a person, draft personalized email, send, store, brief."""

import json
import asyncio
from datetime import date

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from config import MY_EMAIL
from models.contact import create_contact, calculate_next_followup
from prompts.research import RESEARCH_PROMPT
from prompts.email_draft import OUTREACH_EMAIL_PROMPT


def _parse_llm_json(text: str) -> dict:
    """Strip markdown fences and parse JSON from LLM output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()
    return json.loads(cleaned)


class OutboundAgent:
    def __init__(self, inkbox_identity, llm: ChatOpenAI, vault_manager):
        self.identity = inkbox_identity
        self.llm = llm
        self.vault = vault_manager

    async def reach_out(self, name: str, company: str, target_email: str = "") -> dict:
        """Full outbound flow: research -> draft -> send -> store -> brief."""
        try:
            # Step 1: Research
            print(f"  Researching {name} at {company}...")
            research = await self._research(name, company)

            # Step 2: Draft email
            print(f"  Drafting personalized email...")
            email = await self._draft_email(research)

            # Step 3: Determine recipient email
            to_email = target_email or research.get("email", "")
            if not to_email:
                to_email = f"{name.lower().replace(' ', '.')}@{company.lower().replace(' ', '')}.com"

            # Step 4: Send via Inkbox
            print(f"  Sending email to {to_email}...")
            msg = self.identity.send_email(
                to=[to_email],
                subject=email["subject"],
                body_text=email["body"],
            )
            thread_id = str(msg.thread_id) if msg.thread_id else str(msg.id)
            message_id = msg.message_id

            # Step 5: Store in vault
            contact = create_contact(
                name=name,
                email=to_email,
                company=company,
                role=research.get("role", "Unknown"),
                source="outbound",
                context_notes=email.get("angle_used", ""),
                tags=research.get("tech_stack", "").split(", ")[:5] if isinstance(research.get("tech_stack"), str) else [],
            )
            contact["outreach_history"].append({
                "date": date.today().isoformat(),
                "type": "outbound",
                "subject": email["subject"],
                "thread_id": thread_id,
                "message_id": message_id,
                "reply_received": False,
                "sentiment": None,
            })
            contact["next_follow_up"] = calculate_next_followup(7)
            self.vault.store_contact(contact)

            # Step 6: Brief me
            self._send_briefing(name, company, email, research)

            print(f"  Done! Email sent to {to_email}")
            return {"status": "sent", "contact": contact, "email": email, "research": research}

        except Exception as e:
            print(f"  Error in outbound flow: {e}")
            return {"status": "error", "error": str(e)}

    async def _research(self, name: str, company: str) -> dict:
        """Use OpenAI to research the person."""
        prompt = RESEARCH_PROMPT.format(name=name, company=company)
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return _parse_llm_json(response.content)
        except json.JSONDecodeError:
            return {
                "role": "Unknown",
                "recent_work": "Could not find specific details",
                "company_news": f"{company} is active in the industry",
                "tech_stack": "Not available",
                "mutual_interests": "Both work in tech",
                "best_angle": f"Fellow professional at {company}",
                "conversation_starters": [f"Your work at {company}"],
            }

    async def _draft_email(self, research: dict) -> dict:
        """Draft personalized email based on research."""
        prompt = OUTREACH_EMAIL_PROMPT.format(research_json=json.dumps(research, indent=2))
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return _parse_llm_json(response.content)
        except json.JSONDecodeError:
            return {
                "subject": f"Fellow AI engineer — quick hello",
                "body": f"Hi! I'm Paramjeet, an AI/ML engineer graduating from Northeastern. I came across your work at {research.get('company', 'your company')} and thought we might have some interesting overlap. Would you be open to a quick chat?",
                "angle_used": "generic fallback",
            }

    def _send_briefing(self, name: str, company: str, email: dict, research: dict):
        """Email me a summary of what was sent."""
        briefing = (
            f"Outreach sent to {name} at {company}\n\n"
            f"Subject: {email['subject']}\n"
            f"Body: {email['body']}\n\n"
            f"Angle used: {email.get('angle_used', 'N/A')}\n"
            f"Best angle from research: {research.get('best_angle', 'N/A')}\n"
            f"Mutual interests: {research.get('mutual_interests', 'N/A')}"
        )
        try:
            self.identity.send_email(
                to=[MY_EMAIL],
                subject=f"NetWork: Outreach sent to {name} at {company}",
                body_text=briefing,
            )
        except Exception as e:
            print(f"  Warning: Could not send briefing email: {e}")
