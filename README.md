# NetWork — AI Networking Brain

An AI agent that handles your entire professional networking lifecycle using all three Inkbox capabilities: **Email**, **Vault**, and **Phone**.

Built for **Hack-a-Sprint 2026**.

## What it does

| Mode | Description |
|------|-------------|
| **Outbound** | Give it a name + company → researches the person → drafts a hyper-personalized email → sends via Inkbox → stores contact in vault → briefs you |
| **Inbound** | Someone emails your agent → classifies sender (recruiter/founder/networking/agent/spam) → sends intelligent reply → stores contact → briefs you on hot leads |
| **Agent-to-Agent** | Two AI agents on separate Inkbox accounts network with each other, find mutual interests, and propose human connections |
| **Memory & Recall** | Every contact stored in encrypted Inkbox vault with full context. Query by venue, company, warmth score, or free text |
| **Auto Follow-ups** | Detects stale contacts, re-researches for fresh angles, sends threaded follow-ups with warmth-aware strategy |
| **Briefings** | Generates spoken briefing scripts and sends daily summary emails |

## Tech Stack

- **Inkbox SDK** — Email (send/receive/thread), Vault (encrypted CRM), Phone (calls + TTS)
- **LangChain + OpenAI GPT-4o** — Research, drafting, classification, sentiment analysis
- **Flask** — Dashboard API
- **React + Tailwind** — Single-file live dashboard

## Quick Start

```bash
# Clone and set up
cd network
python3.13 -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt

# Add your keys to .env
cp .env.example .env
# Edit .env with your API keys

# Run the agent CLI
python main.py

# Run the dashboard (separate terminal)
python dashboard_api.py
```

## CLI Commands

```
reach out to [name] at [company]  — Personalized outreach
check inbox                       — Process inbound emails
follow up                         — Send follow-ups to stale contacts
agent demo                        — Agent-to-agent networking demo
briefing                          — Get daily briefing
who did I meet at [venue]         — Search contacts
contacts                          — List all contacts
stats                             — Show statistics
```

## Architecture

```
network/
├── config.py            # API keys and settings
├── models/contact.py    # Contact data model
├── prompts/             # 7 LLM prompt templates
├── memory.py            # Vault-backed CRM storage
├── outbound.py          # Research + draft + send
├── inbound.py           # Receive + classify + reply
├── sentiment.py         # Reply sentiment scoring
├── followup.py          # Auto follow-up engine
├── agent_comms.py       # Agent-to-agent networking
├── briefing.py          # Phone/email briefings
├── agent_core.py        # Main orchestrator
├── dashboard_api.py     # Flask API
├── dashboard/index.html # React dashboard
└── main.py              # Entry point
```

## About

Built by **Paramjeet Singh** — AI/ML Engineer, Northeastern University MS '26, CoachMe+ hackathon winner.
