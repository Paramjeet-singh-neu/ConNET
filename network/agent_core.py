"""Main orchestrator — routes user commands to the appropriate agent mode."""

import json
import asyncio

from inkbox import Inkbox
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from config import (
    INKBOX_API_KEY, OPENAI_API_KEY, OPENAI_MODEL, VAULT_KEY,
    AGENT_NAME, AGENT2_NAME, MY_EMAIL, MY_PHONE,
)
from memory import VaultManager
from outbound import OutboundAgent
from inbound import InboundAgent
from sentiment import SentimentAnalyzer
from followup import FollowUpEngine
from agent_comms import AgentCommunicator
from briefing import PhoneBriefing
from smart_intro import SmartIntroEngine


class NetworkAgent:
    def __init__(self):
        print("Initializing NetWork agent...")

        # Inkbox client
        self.inkbox = Inkbox(api_key=INKBOX_API_KEY)
        self.inkbox.__enter__()

        # Primary identity — reuse existing or create
        try:
            self.identity = self.inkbox.get_identity(AGENT_NAME)
            print(f"  Loaded identity: {AGENT_NAME}")
        except Exception:
            self.identity = self.inkbox.create_identity(
                AGENT_NAME,
                create_mailbox=True,
                display_name="NetWork Agent",
            )
            print(f"  Created identity: {AGENT_NAME}")

        # Ensure mailbox
        if not self.identity.mailbox:
            self.identity.create_mailbox()
            print(f"  Created mailbox for {AGENT_NAME}")

        # Second identity info (separate Inkbox account, loaded on demand)
        print(f"  Agent 2 ({AGENT2_NAME}) available for agent-to-agent demo.")

        # LLM
        self.llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.7)

        # Vault
        self.vault = VaultManager(self.inkbox, VAULT_KEY)
        print("  Vault initialized.")

        # Sub-agents
        self.outbound = OutboundAgent(self.identity, self.llm, self.vault)
        self.inbound = InboundAgent(self.identity, self.llm, self.vault)
        self.sentiment = SentimentAnalyzer(self.llm, self.vault)
        self.followup = FollowUpEngine(self.identity, self.llm, self.vault)
        self.agent_comms = AgentCommunicator(self.identity, self.llm, self.vault)
        self.briefing = PhoneBriefing(self.identity, self.llm, self.vault, MY_PHONE)
        self.smart_intro = SmartIntroEngine(self.identity, self.llm, self.vault)

        # Activity counters for briefings
        self.activity = {
            "inbound_count": 0,
            "outbound_count": 0,
            "replies_count": 0,
            "hot_leads": 0,
            "followups_sent": 0,
            "agent_connections": 0,
        }

        print(f"\nNetWork Agent ready!")
        print(f"  Agent email:   {self.identity.email_address}")
        print(f"  Agent 2:       {AGENT2_NAME} (separate Inkbox account)")

    async def handle_command(self, command: str) -> dict:
        """Route user command to appropriate mode."""
        intent = await self._parse_intent(command)
        mode = intent.get("mode", "unknown")

        print(f"\n[Mode: {mode}]")

        if mode == "outbound":
            name = intent.get("name", "")
            company = intent.get("company", "")
            email = intent.get("email", "")
            if not name:
                return {"status": "error", "error": "Please specify a name. Example: 'reach out to John Smith at Google'"}
            result = await self.outbound.reach_out(name, company, email)
            if result.get("status") == "sent":
                self.activity["outbound_count"] += 1
            return result

        elif mode == "check_inbox":
            results = await self.inbound.check_inbox()
            self.activity["inbound_count"] += len(results)
            hot = [r for r in results if r.get("priority") == "hot"]
            self.activity["hot_leads"] += len(hot)
            return {"status": "processed", "count": len(results), "results": results}

        elif mode == "follow_up":
            results = await self.followup.run_follow_ups()
            self.activity["followups_sent"] += len(results)
            return {"status": "followed_up", "count": len(results), "results": results}

        elif mode == "agent_demo":
            result = await self.agent_comms.demo_agent_to_agent()
            self.activity["agent_connections"] += 1
            return result

        elif mode == "briefing":
            return await self.briefing.call_with_briefing(self.activity)

        elif mode == "smart_intro":
            return await self.smart_intro.run_smart_intros(auto_send=False)

        elif mode == "recall":
            query = intent.get("query", command)
            return self._handle_recall(query)

        elif mode == "contacts":
            contacts = self.vault.get_all_contacts()
            return {"status": "ok", "count": len(contacts), "contacts": contacts}

        elif mode == "stats":
            return self._get_stats()

        elif mode == "sentiment":
            # Analyze a specific reply: "analyze sentiment from john@example.com"
            email = intent.get("email", "")
            return {"status": "info", "message": "Sentiment analysis runs automatically on inbound replies. Use 'check inbox' to process new emails."}

        else:
            return {"status": "unknown", "message": f"I didn't understand that. Try: 'reach out to [name] at [company]', 'check inbox', 'follow up', 'agent demo', 'briefing', 'smart intro', 'recall [query]', 'contacts', or 'stats'."}

    async def _parse_intent(self, command: str) -> dict:
        """Use LLM to classify user intent."""
        prompt = f"""Classify this command into one of these modes and extract relevant info.

Modes:
- "outbound": User wants to reach out to someone. Extract "name", "company", and optionally "email".
- "check_inbox": User wants to process new inbound emails.
- "follow_up": User wants to trigger follow-ups for stale contacts.
- "agent_demo": User wants to demo agent-to-agent networking.
- "briefing": User wants a phone briefing / daily summary.
- "recall": User wants to search contacts or memory. Extract "query".
- "contacts": User wants to see all contacts.
- "stats": User wants activity statistics.
- "sentiment": User wants sentiment analysis.
- "smart_intro": User wants to find contacts who should be introduced to each other.

Command: {command}

Return ONLY valid JSON: {{"mode": "...", "name": "...", "company": "...", "email": "...", "query": "..."}}
Fill empty strings for unused fields."""

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            cleaned = response.content.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned.strip())
        except Exception:
            # Fallback: simple keyword matching
            cmd = command.lower().strip()
            if any(w in cmd for w in ["reach out", "email", "send", "contact"]):
                parts = command.split(" at ")
                name = parts[0].replace("reach out to", "").replace("email", "").replace("send to", "").strip()
                company = parts[1].strip() if len(parts) > 1 else ""
                return {"mode": "outbound", "name": name, "company": company, "email": "", "query": ""}
            elif any(w in cmd for w in ["inbox", "check", "inbound"]):
                return {"mode": "check_inbox", "name": "", "company": "", "email": "", "query": ""}
            elif any(w in cmd for w in ["follow", "stale"]):
                return {"mode": "follow_up", "name": "", "company": "", "email": "", "query": ""}
            elif any(w in cmd for w in ["intro", "introduce", "connect them", "match"]):
                return {"mode": "smart_intro", "name": "", "company": "", "email": "", "query": ""}
            elif any(w in cmd for w in ["agent", "demo", "handshake"]):
                return {"mode": "agent_demo", "name": "", "company": "", "email": "", "query": ""}
            elif any(w in cmd for w in ["brief", "call", "phone"]):
                return {"mode": "briefing", "name": "", "company": "", "email": "", "query": ""}
            elif any(w in cmd for w in ["who", "find", "search", "recall", "remember"]):
                return {"mode": "recall", "name": "", "company": "", "email": "", "query": command}
            elif any(w in cmd for w in ["contacts", "list", "all"]):
                return {"mode": "contacts", "name": "", "company": "", "email": "", "query": ""}
            elif any(w in cmd for w in ["stats", "summary", "count"]):
                return {"mode": "stats", "name": "", "company": "", "email": "", "query": ""}
            else:
                return {"mode": "unknown", "name": "", "company": "", "email": "", "query": ""}

    def _handle_recall(self, query: str) -> dict:
        """Search vault for contacts matching a query."""
        contacts = self.vault.search_contacts(query)
        if not contacts:
            return {"status": "no_results", "message": f"No contacts found matching '{query}'."}
        return {
            "status": "found",
            "count": len(contacts),
            "contacts": contacts,
        }

    def _get_stats(self) -> dict:
        """Get activity stats + vault summary."""
        contacts = self.vault.get_all_contacts()
        hot = [c for c in contacts if c.get("warmth_score") == "hot"]
        warm = [c for c in contacts if c.get("warmth_score") == "warm"]
        cold = [c for c in contacts if c.get("warmth_score") == "cold"]
        stale = self.vault.get_stale_contacts()

        return {
            "status": "ok",
            "total_contacts": len(contacts),
            "hot": len(hot),
            "warm": len(warm),
            "cold": len(cold),
            "pending_followups": len(stale),
            "session_activity": self.activity,
        }

    def shutdown(self):
        """Clean up Inkbox client."""
        try:
            self.inkbox.__exit__(None, None, None)
        except Exception:
            pass
