"""ConNET — 2-Minute Demo Runner. Executes all features in sequence."""

import asyncio
import json
import time
import sys

from inkbox import Inkbox
from langchain_openai import ChatOpenAI
from config import (
    INKBOX_API_KEY, OPENAI_API_KEY, OPENAI_MODEL, VAULT_KEY,
    AGENT_NAME, MY_EMAIL, MY_PHONE, INKBOX_API_KEY_2, AGENT2_NAME,
)
from memory import VaultManager
from outbound import OutboundAgent
from inbound import InboundAgent
from agent_comms import AgentCommunicator
from smart_intro import SmartIntroEngine
from conversation import ConversationRecall
from briefing import PhoneBriefing
from live_feed import feed


CYAN = "\033[96m"
GREEN = "\033[92m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def banner(text):
    print(f"\n{BOLD}{CYAN}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}\n")


def pause(label=""):
    input(f"{GREEN}  >> Press ENTER for next step{' — ' + label if label else ''} {RESET}")


def result_line(icon, text):
    print(f"  {icon} {text}")


async def run_demo():
    banner("ConNET — AI Networking Brain")
    print(f"  {DIM}Demo runner — press ENTER to advance through each step.")
    print(f"  Open http://localhost:5050 in your browser before starting.{RESET}")
    print(f"  {DIM}Make sure dashboard_api.py is running in another terminal.{RESET}")
    pause("Start demo recording, then press ENTER")

    # ─── INIT ─────────────────────────────────────────────────
    print(f"\n{DIM}  Initializing agent...{RESET}")
    inkbox = Inkbox(api_key=INKBOX_API_KEY)
    inkbox.__enter__()
    identity = inkbox.get_identity(AGENT_NAME)
    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.7)
    vault = VaultManager(inkbox, VAULT_KEY)
    print(f"  Agent: {BOLD}{identity.agent_handle}{RESET} ({identity.email_address})")
    print(f"  Contacts in vault: {BOLD}{len(vault.get_all_contacts())}{RESET}")

    # ═══════════════════════════════════════════════════════════
    # STEP 1: DASHBOARD OVERVIEW (0:00 - 0:15)
    # ═══════════════════════════════════════════════════════════
    banner("STEP 1: DASHBOARD OVERVIEW")
    print(f"  {BOLD}ACTION:{RESET} Show browser — Network Graph tab first, then Live Feed tab.")
    pause("Show dashboard, then continue")

    # ═══════════════════════════════════════════════════════════
    # STEP 2: OUTBOUND (0:15 - 0:40)
    # ═══════════════════════════════════════════════════════════
    banner("STEP 2: OUTBOUND — Research + Draft + Send")
    pause("Press ENTER to send outreach to Paramjeet Singh")

    outbound = OutboundAgent(identity, llm, vault)
    result = await outbound.reach_out(
        name="Paramjeet Singh",
        company="Northeastern University",
        target_email="singh.para@northeastern.edu",
    )

    if result["status"] == "sent":
        email = result["email"]
        result_line("🚀", f"Email sent to {MY_EMAIL}")
        result_line("📧", f"Subject: {BOLD}{email['subject']}{RESET}")
        result_line("✍️ ", f"Body: {email['body']}")
        result_line("🎯", f"Angle: {email['angle_used']}")
        result_line("🔐", "Contact stored in encrypted vault")
        result_line("📨", "Briefing emailed to you")

    print(f"\n  {BOLD}ACTION:{RESET} Glance at browser Live Feed — outbound event appeared.")
    pause("Continue to inbound")

    # ═══════════════════════════════════════════════════════════
    # STEP 3: INBOUND (0:40 - 1:05)
    # ═══════════════════════════════════════════════════════════
    banner("STEP 3: INBOUND — Receive + Classify + Smart Reply")
    pause("Press ENTER to simulate an inbound email")

    # Send a test email TO the agent
    identity.send_email(
        to=[identity.email_address],
        subject="Founding Engineer Role at NeuralPath AI",
        body_text="Hi Paramjeet, I'm the CTO of NeuralPath AI. We just raised our Series A and need a founding ML engineer to build our RAG infrastructure from scratch. Your CoachMe+ project and production LLM pipeline experience are exactly what we need. Open to chatting this week? — Alex Rivera, CTO, NeuralPath AI",
    )
    result_line("📨", "Inbound email sent to agent...")
    print(f"  {DIM}Waiting for delivery...{RESET}")
    await asyncio.sleep(4)

    # Process inbox
    inbound = InboundAgent(identity, llm, vault)
    results = await inbound.check_inbox()

    if results:
        r = results[0]
        result_line("🏷️ ", f"Classification: {BOLD}{r.get('classification', '?')}{RESET}")
        result_line("🔥", f"Priority: {BOLD}{r.get('priority', '?')}{RESET}")
        result_line("💬", f"Smart reply sent: {r.get('reply_body', '')[:100]}...")
        result_line("🔐", "Contact stored in vault")
        result_line("📨", "Briefing emailed to you")
    else:
        result_line("⚠️ ", "No new inbound (emails may already be read)")

    pause("Continue to agent-to-agent")

    # ═══════════════════════════════════════════════════════════
    # STEP 4: AGENT-TO-AGENT (1:05 - 1:20)
    # ═══════════════════════════════════════════════════════════
    banner("STEP 4: AGENT-TO-AGENT NETWORKING")
    pause("Press ENTER to start agent-to-agent demo")

    comms = AgentCommunicator(identity, llm, vault)
    a2a_result = await comms.demo_agent_to_agent()

    if a2a_result.get("status") == "demo_complete":
        result_line("🤖", f"Agent A: {a2a_result['agent_a_handle']} ({a2a_result['agent_a_email']})")
        result_line("🤖", f"Agent B: {a2a_result['agent_b_handle']} ({a2a_result['agent_b_email']})")
        result_line("🤝", f"Mutual interests: {', '.join(a2a_result.get('mutual_interests', []))}")
        result_line("💡", f"Connection: {a2a_result.get('connection_reason', '?')}")

    pause("Continue to smart intros")

    # ═══════════════════════════════════════════════════════════
    # STEP 5: SMART INTRO (1:20 - 1:35)
    # ═══════════════════════════════════════════════════════════
    banner("STEP 5: SMART INTRO ENGINE")
    pause("Press ENTER to find smart intros")

    intro_engine = SmartIntroEngine(identity, llm, vault)
    intro_result = await intro_engine.run_smart_intros(auto_send=False)

    if intro_result.get("status") == "complete":
        result_line("🔍", f"Scanned contacts — found {intro_result['matches_found']} introduction matches")
        for r in intro_result.get("results", [])[:2]:
            match = r["match"]
            a = match["contact_a"]
            b = match["contact_b"]
            result_line("🤝", f"{a['name']} ({a['company']}) ↔ {b['name']} ({b['company']}) — score: {match['match_score']}/10")
            result_line("  ", f"Reason: {match['reason']}")

    pause("Continue to conversation recall")

    # ═══════════════════════════════════════════════════════════
    # STEP 6: CONVERSATION RECALL (1:35 - 1:47)
    # ═══════════════════════════════════════════════════════════
    banner("STEP 6: CONVERSATION RECALL")
    pause("Press ENTER to recall conversation with Andrew Ng")

    recall = ConversationRecall(identity, vault)
    convo_result = recall.get_conversation("Andrew Ng")

    if convo_result.get("status") == "found":
        for convo in convo_result["conversations"]:
            c = convo["contact"]
            result_line("👤", f"{c['name']} ({c['company']}) [{c['warmth']}]")
            for m in convo["messages"][:3]:
                direction = "→ SENT" if "outbound" in str(m.get("direction", "")).lower() else "← RECEIVED"
                result_line("  ", f"{direction}: {m['subject']}")
                result_line("  ", f'  "{m["body"][:120]}..."')

    pause("Continue to closing — show dashboard")

    # ═══════════════════════════════════════════════════════════
    # STEP 7: CLOSE (1:47 - 2:00)
    # ═══════════════════════════════════════════════════════════
    banner("STEP 7: CLOSING — SHOW DASHBOARD")
    print(f"  {BOLD}ACTION:{RESET} Show browser tabs: Live Feed → Network Graph → Contacts")
    print()
    pause("END — stop recording")

    # Cleanup
    inkbox.__exit__(None, None, None)
    banner("Demo complete! Great job.")


if __name__ == "__main__":
    asyncio.run(run_demo())
