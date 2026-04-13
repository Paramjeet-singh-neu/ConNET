"""NetWork — AI Networking Brain. Entry point."""

import asyncio
import json
import sys
import threading

from agent_core import NetworkAgent


def print_result(result: dict):
    """Pretty-print a command result."""
    status = result.get("status", "unknown")

    if status == "sent":
        email = result.get("email", {})
        contact = result.get("contact", {})
        print(f"\n  ✅ Email sent to {contact.get('name', '?')} at {contact.get('company', '?')}")
        print(f"  Subject: {email.get('subject', '?')}")
        print(f"  Angle: {email.get('angle_used', '?')}")

    elif status == "processed":
        count = result.get("count", 0)
        print(f"\n  ✅ Processed {count} inbound email(s)")
        for r in result.get("results", []):
            cls = r.get("classification", "?")
            pri = r.get("priority", "?")
            print(f"    - {cls} ({pri}): {r.get('briefing_summary', '?')}")

    elif status == "followed_up":
        count = result.get("count", 0)
        print(f"\n  ✅ Sent {count} follow-up(s)")

    elif status == "demo_complete":
        print(f"\n  ✅ Agent-to-agent demo complete!")
        print(f"  Mutual interests: {', '.join(result.get('mutual_interests', []))}")
        print(f"  Connection reason: {result.get('connection_reason', '?')}")

    elif status in ("called", "email_only"):
        print(f"\n  ✅ Briefing {'called + emailed' if status == 'called' else 'emailed (phone unavailable)'}")

    elif status == "found":
        contacts = result.get("contacts", [])
        print(f"\n  Found {len(contacts)} contact(s):")
        for c in contacts:
            warmth = c.get("warmth_score", "?")
            print(f"    - {c['name']} ({c.get('company', '?')}) [{warmth}] — {c.get('context_notes', '')[:60]}")

    elif status == "ok" and "total_contacts" in result:
        # Stats
        print(f"\n  📊 Stats:")
        print(f"    Total contacts: {result['total_contacts']}")
        print(f"    Hot: {result['hot']} | Warm: {result['warm']} | Cold: {result['cold']}")
        print(f"    Pending follow-ups: {result['pending_followups']}")
        act = result.get("session_activity", {})
        print(f"    Session: {act.get('outbound_count', 0)} outbound, {act.get('inbound_count', 0)} inbound, {act.get('followups_sent', 0)} follow-ups")

    elif status == "ok" and "contacts" in result:
        contacts = result.get("contacts", [])
        print(f"\n  {len(contacts)} contact(s) in vault:")
        for c in contacts:
            warmth = c.get("warmth_score", "?")
            print(f"    - {c['name']} ({c.get('company', '?')}) [{warmth}]")

    elif status == "error":
        print(f"\n  ❌ Error: {result.get('error', 'Unknown error')}")

    elif status == "no_results":
        print(f"\n  {result.get('message', 'No results.')}")

    else:
        print(f"\n  {result.get('message', json.dumps(result, indent=2))}")


async def main():
    agent = NetworkAgent()

    print(f"\n{'='*60}")
    print("  NetWork — AI Networking Brain")
    print(f"{'='*60}")
    print(f"\nCommands:")
    print(f"  reach out to [name] at [company]  — Send personalized outreach")
    print(f"  check inbox                       — Process inbound emails")
    print(f"  follow up                         — Send follow-ups to stale contacts")
    print(f"  agent demo                        — Run agent-to-agent networking demo")
    print(f"  briefing                          — Get phone/email briefing")
    print(f"  who did I meet at [venue]          — Search contacts by memory")
    print(f"  contacts                          — List all contacts")
    print(f"  stats                             — Show statistics")
    print(f"  quit                              — Exit\n")

    try:
        while True:
            try:
                command = input("NetWork > ").strip()
            except EOFError:
                break

            if not command:
                continue

            if command.lower() in ("quit", "exit", "q"):
                print("Shutting down NetWork agent...")
                break

            result = await agent.handle_command(command)
            print_result(result)
            print()

    finally:
        agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
