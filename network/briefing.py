"""Phone briefing — generates a script and calls Paramjeet via Inkbox phone with TTS."""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from config import MY_EMAIL
from prompts.briefing_script import BRIEFING_PROMPT
from live_feed import feed


class PhoneBriefing:
    def __init__(self, inkbox_identity, llm: ChatOpenAI, vault_manager, my_phone: str):
        self.identity = inkbox_identity
        self.llm = llm
        self.vault = vault_manager
        self.my_phone = my_phone

    async def call_with_briefing(self, activity_summary: dict) -> dict:
        """Generate briefing script, then attempt phone call. Falls back to email."""
        # Step 1: Generate script
        script = await self._generate_script(activity_summary)
        print(f"\n  Briefing script:\n  \"{script}\"\n")

        # Step 2: Try phone call
        call_success = self._make_call(script)

        # Step 3: Also send as email (backup / record)
        self._send_email_briefing(script, activity_summary)

        feed.log_briefing("phone" if call_success else "email", script)

        return {
            "status": "called" if call_success else "email_only",
            "script": script,
            "activity": activity_summary,
        }

    def _make_call(self, script: str) -> bool:
        """Place call via Inkbox phone. Returns True if successful."""
        try:
            # Check if identity has a phone number
            if not self.identity.phone_number:
                print("  No phone number provisioned. Provisioning one...")
                self.identity.provision_phone_number(type="toll_free")

            # Place the call
            # Note: Inkbox phone uses WebSocket for audio, not simple TTS
            # The call connects and the script would be spoken via WS audio bridge
            # For demo purposes, we place the call and log the script
            call = self.identity.place_call(to_number=self.my_phone)
            print(f"  Phone call placed! Call ID: {call.id}")
            print(f"  Status: {call.status}")
            print(f"  Rate limit: {call.rate_limit.calls_remaining} calls remaining")
            return True

        except Exception as e:
            print(f"  Phone call failed ({e}). Falling back to email briefing.")
            return False

    def _send_email_briefing(self, script: str, activity: dict):
        """Send briefing as email (backup for phone)."""
        body = (
            f"Daily NetWork Briefing\n"
            f"{'=' * 40}\n\n"
            f"Script (what the phone call would say):\n"
            f"\"{script}\"\n\n"
            f"Full Activity Summary:\n"
            f"- Inbound contacts: {activity.get('inbound_count', 0)}\n"
            f"- Outbound sent: {activity.get('outbound_count', 0)}\n"
            f"- Replies received: {activity.get('replies_count', 0)}\n"
            f"- Hot leads: {activity.get('hot_leads', 0)}\n"
            f"- Follow-ups sent: {activity.get('followups_sent', 0)}\n"
            f"- Agent connections: {activity.get('agent_connections', 0)}\n"
        )
        try:
            self.identity.send_email(
                to=[MY_EMAIL],
                subject="NetWork: Daily Briefing",
                body_text=body,
            )
            print("  Briefing email sent!")
        except Exception as e:
            print(f"  Warning: Could not send briefing email: {e}")

    async def _generate_script(self, activity: dict) -> str:
        """Use LLM to create natural-sounding briefing."""
        # Build priority items from vault
        priority_items = []
        try:
            contacts = self.vault.get_all_contacts()
            hot = [c for c in contacts if c.get("warmth_score") == "hot"]
            for c in hot[:3]:
                priority_items.append(f"Hot lead: {c['name']} at {c['company']}")
            stale = self.vault.get_stale_contacts()
            if stale:
                priority_items.append(f"{len(stale)} contacts need follow-up")
        except Exception:
            pass

        prompt = BRIEFING_PROMPT.format(
            inbound_count=activity.get("inbound_count", 0),
            outbound_count=activity.get("outbound_count", 0),
            replies_count=activity.get("replies_count", 0),
            hot_leads=activity.get("hot_leads", 0),
            followups_sent=activity.get("followups_sent", 0),
            agent_connections=activity.get("agent_connections", 0),
            priority_items_json=json.dumps(priority_items),
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip().strip('"')
