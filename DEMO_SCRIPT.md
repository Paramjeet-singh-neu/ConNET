# ConNET Demo Script — 2 Minutes

## Setup Before Recording

Open 3 terminal tabs + 1 browser tab:

**Terminal 1** (Agent CLI):
```bash
cd ~/Downloads/CONNECT/network
source ../venv/bin/activate
python main.py
```

**Terminal 2** (Dashboard):
```bash
cd ~/Downloads/CONNECT/network
source ../venv/bin/activate
python dashboard_api.py
```

**Browser**: Open http://localhost:5050

**Terminal 3** (Keep ready for sending a test email to the agent)

---

## Demo Flow & Script

### 1. INTRO (0:00 - 0:15) — Show: Browser dashboard

> "I'm Paramjeet. I built ConNET — an AI networking agent that handles my entire professional networking lifecycle using Inkbox's email, vault, and phone capabilities. Let me show you what it does."

**Action**: Show the dashboard with the Network Graph tab — the D3 visualization with 15+ contacts.

---

### 2. OUTBOUND (0:15 - 0:40) — Show: Terminal 1 (CLI)

> "First, outbound. I give it a name and company — the agent researches them, drafts a personalized email, and sends it."

**Type in CLI**:
```
reach out to Jensen Huang at NVIDIA
```

**Wait for it to research + draft + send (~8 seconds)**

> "It just researched Jensen Huang, found a specific angle connecting his work to mine, drafted a personalized email under 300 characters, sent it via Inkbox, stored the contact in the encrypted vault, and emailed me a briefing. All in seconds."

**Action**: Switch to browser, show Live Feed tab — the outbound event should appear.

---

### 3. INBOUND (0:40 - 1:05) — Show: Terminal 3, then Terminal 1

> "Now let's flip it. Someone emails my agent — watch what happens."

**In Terminal 3, run**:
```bash
cd ~/Downloads/CONNECT/network && source ../venv/bin/activate && python -c "
from inkbox import Inkbox
from config import INKBOX_API_KEY, AGENT_NAME
with Inkbox(api_key=INKBOX_API_KEY) as inkbox:
    identity = inkbox.get_identity(AGENT_NAME)
    identity.send_email(
        to=[identity.email_address],
        subject='Founding Engineer Role at AI Startup',
        body_text='Hi Paramjeet, I am the CTO of NeuralPath AI. We just raised our Series A and are looking for a founding ML engineer to build our RAG infrastructure. Your CoachMe+ project caught my eye. Interested in chatting this week?',
    )
    print('Email sent to agent!')
"
```

**Switch to Terminal 1, type**:
```
check inbox
```

> "It classified the sender as a founder, scored it as hot priority, sent an intelligent reply expressing interest, stored the contact, and briefed me. My inbox is now an AI gatekeeper."

---

### 4. AGENT-TO-AGENT (1:05 - 1:20) — Show: Terminal 1

> "Here's what nobody else built. I have two separate Inkbox agent identities. Watch them network with each other."

**Type in CLI**:
```
agent demo
```

> "Agent A just introduced itself to Agent B, they exchanged info about their humans, found mutual interests, and proposed a connection. This is the future — AI agents networking on behalf of people."

---

### 5. SMART INTRO (1:20 - 1:35) — Show: Terminal 1

> "ConNET also finds people in my network who should know each other."

**Type in CLI**:
```
smart intro
```

> "It scanned all my contacts, evaluated every pair for mutual interests, scored compatibility, and drafted warm introduction emails. I'm not just networking — I'm creating connections between others."

---

### 6. CONVERSATION RECALL (1:35 - 1:47) — Show: Terminal 1

> "Six months from now, I forget what I discussed with someone. No problem."

**Type in CLI**:
```
convo Andrew Ng
```

> "Full conversation pulled from Inkbox — every email I sent and received, with the complete message body. My networking memory never fades."

---

### 7. DASHBOARD + CLOSE (1:47 - 2:00) — Show: Browser

**Action**: Show all 3 tabs quickly — Live Feed (events streaming), Network Graph (interactive nodes), Contacts (cards with warmth scores).

> "Everything is live on the dashboard — real-time activity feed, an interactive network graph, and contact cards with warmth scores. Email, vault, phone — all three Inkbox capabilities working together as a complete AI networking brain. That's ConNET."

---

## Tips
- Keep the CLI visible and large font (Cmd + to zoom terminal)
- Have the dashboard open before recording
- The Live Feed tab is the most impressive to show during actions
- Split screen: terminal on left, browser on right if possible
