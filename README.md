# ConNET — AI Networking Brain

> An AI agent that sends personalized outreach, qualifies inbound contacts, networks with other AI agents, remembers everyone you've ever met, and briefs you daily.

Built with **Inkbox SDK** (Email + Vault + Phone) | **LangChain + GPT-4o** | **Flask + React + D3.js**


---

## Screenshots

### Network Graph
Interactive D3.js force-directed visualization — you at the center (purple), contacts color-coded by warmth.

<img width="1470" height="826" alt="Screenshot 2026-04-15 at 12 16 30 AM" src="https://github.com/user-attachments/assets/543819ce-71aa-4e88-8ed8-cddad6a66eee" />


### Contacts Dashboard
Contact cards with warmth badges, outreach timelines, tags, and follow-up schedules.

<img width="1470" height="826" alt="Screenshot 2026-04-15 at 12 16 59 AM" src="https://github.com/user-attachments/assets/4c9f11d7-50f3-4f6c-9bbf-c2f403d07560" />


### Agent CLI
Natural language commands to trigger outbound outreach, inbox checks, agent demos, and more.

<img width="1470" height="849" alt="Screenshot 2026-04-15 at 12 42 54 AM" src="https://github.com/user-attachments/assets/a5ba9167-d093-4455-ac8b-d54016d1d4ab" />


---

## The Problem

Networking is a full-time job. You meet people at events, exchange emails, forget to follow up, lose context on conversations, and miss connections between people in your own network. No tool handles the complete lifecycle.

## The Solution

ConNET is an AI agent with its own email address and encrypted memory. Give it a name — it researches the person, sends a personalized email, tracks the relationship, follows up automatically, and even finds people in your network who should know each other.

---

## Features

### 1. Outbound Outreach
Give it a name + company. The agent researches them with GPT-4o, drafts a hyper-personalized email under 300 characters, sends it via Inkbox, stores the contact in encrypted vault, and emails you a briefing.

### 2. Inbound Gatekeeper
Your agent has a public email address. When someone emails it, the agent classifies the sender (recruiter / founder / networking / agent / spam), sends an intelligent reply, stores the contact, and alerts you about hot leads.

### 3. Agent-to-Agent Networking
Two AI agents on **separate Inkbox accounts** introduce their humans to each other, exchange structured info, find mutual interests, and propose connections. The future of AI-to-AI networking.

### 4. Smart Intro Engine
Scans all your contacts, evaluates every pair for mutual interests and collaboration potential, scores compatibility 1-10, and drafts warm double-opt-in introduction emails. You don't just network — you create connections between others.

### 5. Conversation Recall
Forgot what you discussed with someone from 6 months ago? Ask the agent — it pulls the full email thread from Inkbox with complete message bodies. Your networking memory never fades.

### 6. Sentiment-Aware Follow-ups
Analyzes reply sentiment (enthusiasm, specificity, next-step signals) to classify contacts as hot / warm / cold. Hot leads get fast, direct follow-ups. Cold leads get one final soft touch. Max 3 attempts per contact.

### 7. Live Dashboard
Three-tab real-time dashboard:
- **Live Feed** — Server-Sent Events stream showing every agent action as it happens
- **Network Graph** — Interactive D3.js force-directed visualization with warmth-coded nodes
- **Contacts** — Card view with outreach timelines, tags, and follow-up schedules

### 8. Daily Briefings
Generates a spoken briefing script and sends a summary email covering all agent activity — new contacts, hot leads, follow-ups sent, and agent connections.

---

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │              ConNET Agent CLI                │
                    │              (main.py)                       │
                    └──────────────────┬──────────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────────┐
                    │           Agent Core (Orchestrator)          │
                    │           Intent parsing + routing           │
                    └──┬───┬───┬───┬───┬───┬───┬───┬─────────────┘
                       │   │   │   │   │   │   │   │
          ┌────────────┘   │   │   │   │   │   │   └────────────┐
          ▼                ▼   │   ▼   │   ▼   │                ▼
    ┌──────────┐   ┌─────────┐│ ┌─────┐│ ┌─────┐│   ┌───────────────┐
    │ Outbound │   │ Inbound ││ │Smart││ │Convo││   │   Briefing    │
    │ Research │   │Classify ││ │Intro││ │Recall││   │  Phone/Email  │
    │  Draft   │   │  Reply  ││ │Match││ │Thread││   │    TTS        │
    │  Send    │   │  Store  ││ │Draft││ │Fetch ││   └───────────────┘
    └──────────┘   └─────────┘│ └─────┘│ └─────┘│
                              │        │        │
                    ┌─────────▼┐ ┌─────▼────┐ ┌─▼──────────┐
                    │ Sentiment│ │ Follow-up │ │ Agent-to-  │
                    │ Analysis │ │  Engine   │ │   Agent    │
                    │ hot/warm │ │ Re-research│ │ 2 Inkbox  │
                    │  /cold   │ │ Threaded  │ │ Identities│
                    └──────────┘ └──────────┘ └────────────┘
                              │        │        │
          ┌───────────────────┼────────┼────────┘
          ▼                   ▼        ▼
    ┌──────────────────────────────────────────────┐
    │              Inkbox SDK Layer                  │
    │  ┌─────────┐  ┌──────────┐  ┌──────────┐    │
    │  │  Email   │  │  Vault   │  │  Phone   │    │
    │  │Send/Recv │  │Encrypted │  │Calls/TTS │    │
    │  │Threading │  │  CRM     │  │Transcripts│   │
    │  └─────────┘  └──────────┘  └──────────┘    │
    └──────────────────────────────────────────────┘
          │                   │
          ▼                   ▼
    ┌──────────────┐   ┌───────────────────────────┐
    │  LangChain   │   │     Live Dashboard         │
    │  + GPT-4o    │   │  ┌────────┬───────┬──────┐│
    │  7 Prompt    │   │  │Live    │Network│Cards ││
    │  Templates   │   │  │Feed   │Graph  │View  ││
    └──────────────┘   │  │(SSE)  │(D3.js)│      ││
                       │  └────────┴───────┴──────┘│
                       │  Flask API + React/Tailwind│
                       └───────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Communication | Inkbox SDK — Email (send/receive/thread), Vault (encrypted storage), Phone |
| AI | LangChain + OpenAI GPT-4o — research, drafting, classification, sentiment |
| Backend | Flask — REST API + SSE streaming |
| Frontend | React (CDN) + Tailwind CSS + D3.js — live dashboard |
| Language | Python 3.11+ |

---

## Quick Start

```bash
# Clone
git clone https://github.com/Paramjeet-singh-neu/ConNET.git
cd ConNET/network

# Set up environment
python3.11 -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your Inkbox + OpenAI API keys

# Run the agent
python main.py

# Run the dashboard (separate terminal)
python dashboard_api.py
# Open http://localhost:5050
```

### Real-time webhooks, SMS, and live phone (optional)

ConNET vendors the [Inkbox sample client/server](https://github.com/inkbox-ai/sample-client-server) under `vendor/inkbox-sample-client-server/`. Running it gives you:

- **`POST /webhook`** — signed mail, SMS, and incoming-call webhooks (same endpoint as upstream).
- **`WebSocket /phone/media/ws`** — live calls with Inkbox STT/TTS and the sample phone agent.
- **Inkbox tunnel** — bootstrap patches your identity’s mailbox and phone number to the tunnel hostname (see the vendor `README.md`).

Install gateway dependencies, add signing key + tunnel name to `.env`, then start the gateway from `network/`:

```bash
pip install -r requirements.txt -r requirements-inkbox-gateway.txt
# .env: INKBOX_SIGNING_KEY, INKBOX_TUNNEL_NAME (plus existing INKBOX_API_KEY, OPENAI_API_KEY, …)
python run_inkbox_gateway.py
```

With `CONNET_WEBHOOK_INTEGRATION` enabled (the default when using `run_inkbox_gateway.py`), inbound **`message.received`** mail webhooks run the same classify / reply / vault flow as `check inbox` in the CLI. Inbound SMS is logged to the live feed; you can extend `connet_webhook_hook.py` to automate replies. The CLI `check inbox` path remains useful for local testing without the tunnel. The upstream sample targets **Python 3.12+**; use a 3.12+ venv if the gateway fails to install on older Python.

---

## CLI Commands

```
reach out to [name] at [company]    Personalized outreach
check inbox                         Process inbound emails
follow up                           Send follow-ups to stale contacts
agent demo                          Agent-to-agent networking demo
smart intro                         Find contacts who should meet
convo [name]                        Recall conversation with someone
briefing                            Get daily briefing
who did I meet at [venue]           Search contacts by memory
contacts                            List all contacts
stats                               Show statistics
```

---

## File Structure

```
network/
├── main.py               Entry point — interactive CLI
├── run_inkbox_gateway.py  Inkbox tunnel + webhooks + phone WS (vendored sample + ConNET hooks)
├── connet_webhook_hook.py Webhook → InboundAgent bridge for mail / SMS logging
├── org_context.py         Inkbox org Contacts + Notes context for inbound qualify
├── agent_core.py          Orchestrator — intent routing to all modes
├── outbound.py            Research + personalized email + send
├── inbound.py             Inbox polling + classification + smart reply
├── agent_comms.py         Agent-to-agent networking (2 Inkbox identities)
├── smart_intro.py         Find mutual connections + draft intros
├── conversation.py        Pull full email threads from Inkbox
├── sentiment.py           Reply sentiment scoring (hot/warm/cold)
├── followup.py            Auto follow-up engine with fresh research
├── memory.py              Vault-backed encrypted CRM
├── briefing.py            Phone/email daily briefings
├── live_feed.py           SSE event stream for real-time dashboard
├── dashboard_api.py       Flask API + SSE endpoints
├── dashboard/index.html   React + D3.js single-page dashboard
├── config.py              Environment config
├── requirements.txt       Core Python dependencies
├── requirements-inkbox-gateway.txt  Optional: vendored Inkbox webhook + phone server
├── models/contact.py      Contact data model
└── prompts/               7 LLM prompt templates
```

---

## How It Uses Inkbox

| Capability | How ConNET Uses It |
|-----------|-------------------|
| **Email — Send** | Outbound outreach, smart replies, follow-ups, intro emails, briefings |
| **Email — Receive** | Inbox polling (`check inbox`), or real-time **webhooks** via `run_inkbox_gateway.py` + `connet_webhook_hook.py` |
| **Email — Threading** | Follow-ups in same thread, conversation recall with full bodies |
| **Vault** | Encrypted CRM storing contacts with warmth scores, outreach history, and follow-up schedules |
| **Org Contacts / Notes** | Reverse-lookup + note search enrich inbound classification (`org_context.py`); vCard import via `import vcards …` (Inkbox SDK 0.3+) |
| **Phone** | Daily briefing calls; optional **vendored gateway** answers live inbound calls (Inkbox STT/TTS + sample agent) |
| **Identity** | Two separate agent identities for agent-to-agent networking demo |

---

## What Makes This Different

- **Uses all 3 Inkbox capabilities** — Email, Vault, and Phone working together as a system
- **Agent-to-Agent networking** — two real Inkbox identities exchanging structured info autonomously
- **Smart Intro Engine** — AI finding connections *between* your contacts, not just managing them
- **Conversation Recall** — full email threads pulled from Inkbox, not just metadata
- **Live Dashboard** — real-time SSE feed + interactive D3.js network graph
- **Solves a real problem** — built by a job-searching grad student who actually needs this tool

---

## Built By

**Paramjeet Singh**
- AI/ML Engineer | MS in Information Systems, Northeastern University '26
- 3+ years building LLM pipelines, RAG systems, and agentic AI in production

[LinkedIn](https://linkedin.com/in/paramjeetsingh31) | [GitHub](https://github.com/Paramjeet-singh-neu)
