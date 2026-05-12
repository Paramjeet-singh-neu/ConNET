QUALIFY_PROMPT = """You manage Paramjeet's networking inbox. Classify this inbound email and draft a response.

From: {sender_email}
Subject: {subject}
Body: {body}

Org address book (Inkbox Contacts reverse-lookup — prefer these names/companies over guessing from the From header alone):
{org_contacts}

Inkbox Notes visible to this agent (snippets from search on sender email / domain — use as relationship context):
{org_notes}

Step 1 — Classify: "recruiter" | "founder" | "networking" | "agent" | "spam"
Step 2 — Priority: "hot" | "warm" | "cold"
Step 3 — Draft reply:
- Recruiter/founder: Express interest, ask about the role
- Networking: Be friendly, find common ground
- Agent: Respond with structured data about Paramjeet
- Spam: No reply

Return JSON:
{{
    "classification": "recruiter|founder|networking|agent|spam",
    "priority": "hot|warm|cold",
    "reply_needed": true,
    "reply_subject": "Re: ...",
    "reply_body": "response text",
    "vault_entry": {{"name": "extracted name or Unknown", "company": "extracted company or Unknown", "context_notes": "summary of what they want"}},
    "briefing_summary": "one-line summary for Paramjeet"
}}"""
