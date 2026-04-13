"""Mode 3: Agent-to-Agent networking — two real AI agents on separate Inkbox accounts."""

import json
import asyncio
from datetime import date

from inkbox import Inkbox
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from config import MY_EMAIL, INKBOX_API_KEY_2, AGENT2_NAME
from models.contact import create_contact
from prompts.agent_handshake import AGENT_HANDSHAKE_PROMPT


def _parse_llm_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


class AgentCommunicator:
    def __init__(self, identity_a, llm: ChatOpenAI, vault_manager):
        self.agent_a = identity_a
        self.llm = llm
        self.vault = vault_manager

    def _get_agent_b(self):
        """Open a separate Inkbox client for the second agent."""
        inkbox_b = Inkbox(api_key=INKBOX_API_KEY_2)
        inkbox_b.__enter__()
        identity_b = inkbox_b.get_identity(AGENT2_NAME)
        return inkbox_b, identity_b

    async def initiate_handshake(self, target_agent_email: str) -> dict:
        """Send initial agent-to-agent introduction."""
        print(f"  Agent A initiating handshake with {target_agent_email}...")

        intro = await self._generate_message(mode="initiating", agent_message="")

        self.agent_a.send_email(
            to=[target_agent_email],
            subject="[Agent-to-Agent] NetWork Introduction",
            body_text=intro["response_to_agent"],
        )

        print(f"  Handshake sent!")
        return intro

    async def respond_to_agent(self, incoming_email: dict) -> dict:
        """Respond to another agent's introduction."""
        print(f"  Responding to agent from {incoming_email['from']}...")

        result = await self._generate_message(
            mode="responding",
            agent_message=incoming_email["body"],
        )

        self.agent_a.send_email(
            to=[incoming_email["from"]],
            subject=f"Re: {incoming_email['subject']}",
            body_text=result["response_to_agent"],
            in_reply_to_message_id=incoming_email.get("message_id"),
        )

        vault_entry = result.get("vault_entry", {})
        contact = create_contact(
            name=vault_entry.get("name", "Unknown Agent Contact"),
            email=incoming_email["from"],
            company=vault_entry.get("company", "Unknown"),
            source="agent",
            context_notes=vault_entry.get("context_notes", "Connected via agent-to-agent networking"),
        )
        self.vault.store_contact(contact)

        self._brief_paramjeet(result)
        return result

    async def demo_agent_to_agent(self) -> dict:
        """Demo: Agent A (paramjeet-agent) and Agent B (testAgent) network with each other."""
        print("  Starting agent-to-agent demo...")
        print(f"  Agent A: {self.agent_a.agent_handle} ({self.agent_a.email_address})")

        # Connect to second agent
        inkbox_b, agent_b = self._get_agent_b()
        print(f"  Agent B: {agent_b.agent_handle} ({agent_b.email_address})")

        try:
            # Step 1: Agent A introduces itself to Agent B
            print("\n  Step 1: Agent A sends introduction to Agent B...")
            intro = await self._generate_message(mode="initiating", agent_message="")

            msg_a = self.agent_a.send_email(
                to=[agent_b.email_address],
                subject="[Agent-to-Agent] NetWork Introduction",
                body_text=intro["response_to_agent"],
            )
            print(f"  Sent! Message ID: {msg_a.id}")

            await asyncio.sleep(3)

            # Step 2: Agent B generates response and replies
            print("\n  Step 2: Agent B responds to Agent A...")
            response = await self._generate_message(
                mode="responding",
                agent_message=intro["response_to_agent"],
            )

            msg_b = agent_b.send_email(
                to=[self.agent_a.email_address],
                subject="Re: [Agent-to-Agent] NetWork Introduction",
                body_text=response["response_to_agent"],
                in_reply_to_message_id=msg_a.message_id,
            )
            print(f"  Replied! Message ID: {msg_b.id}")

            # Step 3: Store the connection in vault
            vault_entry = response.get("vault_entry", {})
            contact = create_contact(
                name=vault_entry.get("name", "Agent B's Human"),
                email=agent_b.email_address,
                company=vault_entry.get("company", "Demo Partner"),
                source="agent",
                context_notes=vault_entry.get("context_notes", "Agent-to-agent demo connection"),
            )
            self.vault.store_contact(contact)

            # Step 4: Brief Paramjeet
            self._brief_paramjeet(response)

            result = {
                "status": "demo_complete",
                "agent_a_handle": self.agent_a.agent_handle,
                "agent_a_email": self.agent_a.email_address,
                "agent_b_handle": agent_b.agent_handle,
                "agent_b_email": agent_b.email_address,
                "agent_a_sent": intro,
                "agent_b_replied": response,
                "mutual_interests": response.get("mutual_interests", []),
                "connection_reason": response.get("connection_reason", ""),
            }
            print("\n  Agent-to-agent demo complete!")
            return result

        finally:
            inkbox_b.__exit__(None, None, None)

    async def _generate_message(self, mode: str, agent_message: str) -> dict:
        """Generate agent handshake message using LLM."""
        prompt = AGENT_HANDSHAKE_PROMPT.format(
            mode=mode,
            agent_message=agent_message or "(initiating contact — no prior message)",
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return _parse_llm_json(response.content)
        except json.JSONDecodeError:
            return {
                "response_to_agent": "Hello! I'm NetWork, Paramjeet's AI networking agent. Paramjeet is an AI/ML Engineer at Northeastern, winner of the Voxel51 hackathon. Let's explore how our humans might connect!",
                "mutual_interests": ["AI/ML", "technology"],
                "connection_reason": "Both involved in AI and technology",
                "briefing_for_paramjeet": "Agent-to-agent connection initiated",
                "vault_entry": {"name": "Unknown", "company": "Unknown", "source": "agent", "context_notes": "Agent handshake"},
            }

    def _brief_paramjeet(self, result: dict):
        """Send briefing email about agent-to-agent connection."""
        briefing = (
            f"Agent-to-Agent Connection!\n\n"
            f"Connection reason: {result.get('connection_reason', 'N/A')}\n"
            f"Mutual interests: {', '.join(result.get('mutual_interests', []))}\n"
            f"Summary: {result.get('briefing_for_paramjeet', 'N/A')}\n"
        )
        try:
            self.agent_a.send_email(
                to=[MY_EMAIL],
                subject="NetWork: New Agent-to-Agent Connection",
                body_text=briefing,
            )
        except Exception as e:
            print(f"  Warning: Could not send briefing: {e}")
