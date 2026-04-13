# ConNET — AI Networking Brain

An AI agent that handles your entire professional networking lifecycle using all three Inkbox capabilities: **Email**, **Vault**, and **Phone**.

Built for **Hack-a-Sprint 2026**.

## What it does

| Mode | Description |
|------|-------------|
| **Outbound** | Give it a name + company -> researches the person -> drafts a hyper-personalized email -> sends via Inkbox -> stores contact in vault -> briefs you |
| **Inbound** | Someone emails your agent -> classifies sender (recruiter/founder/networking/agent/spam) -> sends intelligent reply -> stores contact -> briefs you on hot leads |
| **Agent-to-Agent** | Two AI agents on separate Inkbox accounts network with each other, find mutual interests, and propose human connections |
| **Memory & Recall** | Every contact stored in encrypted Inkbox vault with full context. Query by venue, company, warmth score, or free text |
| **Auto Follow-ups** | Detects stale contacts, re-researches for fresh angles, sends threaded follow-ups with warmth-aware strategy |
| **Smart Intros** | Scans your network, finds contacts who should know each other, scores compatibility, and drafts warm double-opt-in introduction emails |
| **Briefings** | Generates spoken briefing scripts and sends daily summary emails |

## Standout Features

### Live Activity Feed
Real-time Server-Sent Events (SSE) stream on the dashboard. Every agent action — outbound emails, inbound classifications, smart replies, sentiment scores, follow-ups — appears instantly. During a demo, judges can email the agent and watch the dashboard light up live.

### Network Graph
Interactive D3.js force-directed visualization of your entire contact network. You sit at the center (purple), surrounded by contacts color-coded by warmth (red = hot, orange = warm, blue = cold). Contacts at the same company or venue are linked together. Fully draggable and interactive.

### Smart Intro Engine
AI scans all your contacts, evaluates every pair for mutual interests, complementary skills, and collaboration potential. Scores matches 1-10, then drafts warm introduction emails connecting people who should meet. Nobody else is using AI to create connections *between* their contacts.

## Tech Stack

- **Inkbox SDK** — Email (send/receive/thread), Vault (encrypted CRM), Phone (calls + TTS)
- **LangChain + OpenAI GPT-4o** — Research, drafting, classification, sentiment analysis
- **Flask** — Dashboard API with SSE streaming
- **React + Tailwind + D3.js** — Live dashboard with network graph

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
smart intro                       — Find contacts who should meet
briefing                          — Get daily briefing
who did I meet at [venue]         — Search contacts
contacts                          — List all contacts
stats                             — Show statistics
```

## Dashboard

Three-tab layout at `http://localhost:5050`:

- **Live Feed** — Real-time activity stream with SSE
- **Network Graph** — D3.js force-directed contact visualization
- **Contacts** — Card view with warmth scores, outreach timelines, and tags

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
├── smart_intro.py       # Smart introduction engine
├── live_feed.py         # Real-time SSE activity feed
├── briefing.py          # Phone/email briefings
├── agent_core.py        # Main orchestrator
├── dashboard_api.py     # Flask API with SSE
├── dashboard/index.html # React + D3.js dashboard
└── main.py              # Entry point
```

## About

Built by **Paramjeet Singh** — AI/ML Engineer, Northeastern University MS '26, CoachMe+ hackathon winner.
