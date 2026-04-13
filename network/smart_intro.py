"""Smart Intro Engine — scans vault contacts, finds who should know each other, drafts warm introductions."""

import json
import asyncio
from itertools import combinations

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from config import MY_EMAIL
from live_feed import feed


INTRO_MATCH_PROMPT = """You are analyzing two contacts from Paramjeet's professional network to determine if they should be introduced to each other.

Contact A:
{contact_a_json}

Contact B:
{contact_b_json}

Evaluate whether these two people would benefit from knowing each other.
Consider: overlapping industries, complementary skills, shared interests, potential collaboration, same city/event, hiring/job-seeking alignment.

Return JSON:
{{
    "should_introduce": true/false,
    "match_score": 0-10,
    "reason": "one sentence explaining why they should connect",
    "shared_interests": ["list of overlaps"],
    "intro_angle": "the specific hook for the introduction"
}}"""

INTRO_DRAFT_PROMPT = """Draft a warm double-opt-in introduction email from Paramjeet connecting two people in his network.

Person A: {person_a_name} ({person_a_company}) — {person_a_context}
Person B: {person_b_name} ({person_b_company}) — {person_b_context}
Reason to connect: {reason}
Shared interests: {shared_interests}

Rules:
- Email goes to BOTH people (CC'd)
- Reference how Paramjeet knows each person
- State the specific reason they should connect
- Warm, concise, not corporate
- Under 200 words
- End with "I'll let you two take it from here"

Return JSON:
{{
    "subject": "Intro: [Person A] ↔ [Person B]",
    "body": "email body text",
    "confidence": "high|medium|low"
}}"""


def _parse_llm_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


class SmartIntroEngine:
    def __init__(self, inkbox_identity, llm: ChatOpenAI, vault_manager):
        self.identity = inkbox_identity
        self.llm = llm
        self.vault = vault_manager

    async def find_intros(self) -> list[dict]:
        """Scan all contacts and find pairs that should be introduced."""
        contacts = self.vault.get_all_contacts()

        if len(contacts) < 2:
            print("  Need at least 2 contacts for smart intros.")
            return []

        print(f"  Scanning {len(contacts)} contacts for introduction opportunities...")

        # Evaluate all pairs (limit to avoid API overload)
        pairs = list(combinations(contacts, 2))[:10]
        matches = []

        for a, b in pairs:
            # Skip if same email
            if a.get("email") == b.get("email"):
                continue

            match = await self._evaluate_pair(a, b)
            if match.get("should_introduce") and match.get("match_score", 0) >= 6:
                match["contact_a"] = a
                match["contact_b"] = b
                matches.append(match)
                print(f"    Match found: {a['name']} ↔ {b['name']} (score: {match['match_score']})")

            await asyncio.sleep(0.5)

        # Sort by match score
        matches.sort(key=lambda m: m.get("match_score", 0), reverse=True)

        print(f"  Found {len(matches)} introduction opportunities.")
        return matches

    async def draft_and_send_intro(self, match: dict, send: bool = True) -> dict:
        """Draft and optionally send an introduction email."""
        a = match["contact_a"]
        b = match["contact_b"]

        print(f"  Drafting intro: {a['name']} ↔ {b['name']}...")

        email = await self._draft_intro(a, b, match)

        if send and email.get("confidence") != "low":
            # Send to both as a BCC to Paramjeet
            recipients = []
            if a.get("email"):
                recipients.append(a["email"])
            if b.get("email"):
                recipients.append(b["email"])

            if recipients:
                try:
                    self.identity.send_email(
                        to=recipients,
                        subject=email["subject"],
                        body_text=email["body"],
                        bcc=[MY_EMAIL],
                    )
                    print(f"    Intro email sent to {', '.join(recipients)}")

                    feed.log_intro(a["name"], b["name"], match.get("reason", ""))

                except Exception as e:
                    print(f"    Error sending intro: {e}")
                    return {"status": "error", "error": str(e), "email": email}

                return {"status": "sent", "email": email, "match": match}

        return {"status": "drafted", "email": email, "match": match}

    async def run_smart_intros(self, auto_send: bool = False) -> dict:
        """Full flow: find matches, draft intros, optionally send."""
        matches = await self.find_intros()

        if not matches:
            return {"status": "no_matches", "message": "No strong introduction matches found."}

        results = []
        for match in matches[:3]:  # Top 3 matches
            result = await self.draft_and_send_intro(match, send=auto_send)
            results.append(result)
            await asyncio.sleep(1)

        return {
            "status": "complete",
            "matches_found": len(matches),
            "intros_processed": len(results),
            "results": results,
        }

    async def _evaluate_pair(self, a: dict, b: dict) -> dict:
        """Use LLM to evaluate if two contacts should be introduced."""
        # Slim down contact data for the prompt
        slim_a = {k: a.get(k, "") for k in ["name", "company", "role", "context_notes", "tags", "warmth_score", "venue"]}
        slim_b = {k: b.get(k, "") for k in ["name", "company", "role", "context_notes", "tags", "warmth_score", "venue"]}

        prompt = INTRO_MATCH_PROMPT.format(
            contact_a_json=json.dumps(slim_a, indent=2),
            contact_b_json=json.dumps(slim_b, indent=2),
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return _parse_llm_json(response.content)
        except json.JSONDecodeError:
            return {"should_introduce": False, "match_score": 0}

    async def _draft_intro(self, a: dict, b: dict, match: dict) -> dict:
        """Draft the introduction email."""
        prompt = INTRO_DRAFT_PROMPT.format(
            person_a_name=a["name"],
            person_a_company=a.get("company", ""),
            person_a_context=a.get("context_notes", ""),
            person_b_name=b["name"],
            person_b_company=b.get("company", ""),
            person_b_context=b.get("context_notes", ""),
            reason=match.get("reason", ""),
            shared_interests=", ".join(match.get("shared_interests", [])),
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return _parse_llm_json(response.content)
        except json.JSONDecodeError:
            return {
                "subject": f"Intro: {a['name']} ↔ {b['name']}",
                "body": f"Hey! I wanted to connect you two. {a['name']} ({a.get('company','')}) and {b['name']} ({b.get('company','')}) — {match.get('reason', 'I think you have a lot in common')}. I'll let you two take it from here!",
                "confidence": "low",
            }
