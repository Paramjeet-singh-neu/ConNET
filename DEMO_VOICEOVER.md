# ConNET Live Demo — Commands + Script

---

## SETUP — Run these before the demo starts

### Terminal 1 (Dashboard):
```bash
cd ~/Downloads/CONNECT/network && source ../venv/bin/activate && python dashboard_api.py
```

### Terminal 2 (Agent CLI):
```bash
cd ~/Downloads/CONNECT/network && source ../venv/bin/activate && python main.py
```

### Browser:
Open http://localhost:5050 — start on Network Graph tab

---

## STEP 1 — INTRO (show dashboard)

---

## STEP 2 — OUTBOUND (type in Terminal 2)

```
reach out to Paramjeet Singh at Northeastern University
```

First, outbound outreach. I give the agent a name and company. It researches them using GPT-4o, drafts a hyper-personalized email under 300 characters, sends it through Inkbox, stores the contact in the encrypted vault, and emails me a briefing. All of that just happened in a few seconds — you can see the result right here.

---

## STEP 3 — INBOUND (send test email, then check inbox)

### First, open Terminal 3 and run this to simulate an inbound email:
```bash
cd ~/Downloads/CONNECT/network && source ../venv/bin/activate && python -c "
from inkbox import Inkbox
from config import INKBOX_API_KEY, AGENT_NAME
with Inkbox(api_key=INKBOX_API_KEY) as inkbox:
    identity = inkbox.get_identity(AGENT_NAME)
    identity.send_email(
        to=[identity.email_address],
        subject='Founding Engineer Role at NeuralPath AI',
        body_text='Hi Paramjeet, I am the CTO of NeuralPath AI. We just raised our Series A and need a founding ML engineer to build our RAG infrastructure. Your CoachMe+ project caught my eye. Open to chatting this week? — Alex Rivera, CTO',
    )
    print('Email sent!')
"
```

### Wait 5 seconds, then type in Terminal 2:
```
check inbox
```

Now let's flip it. Someone emails my agent. The agent reads the message, classifies the sender — in this case it identified a founder with a hot priority — sent an intelligent reply expressing interest, stored the contact in vault, and briefed me. My inbox is now an AI gatekeeper.

---

## STEP 4 — AGENT-TO-AGENT (type in Terminal 2)

```
agent demo
```

Here's what makes this project unique. I have two separate Inkbox agent identities. Watch them network with each other. Agent A just introduced itself to Agent B, they exchanged structured information about their humans, found mutual interests, and proposed a connection. This is AI-to-AI networking.

---

## STEP 5 — SMART INTROS (type in Terminal 2)

```
smart intro
```

ConNET also finds people in my network who should know each other. It just scanned all my contacts, evaluated every pair for mutual interests and collaboration potential, scored compatibility, and drafted warm introduction emails. I'm not just networking — I'm creating connections between others.

---

## STEP 6 — CONVERSATION RECALL (type in Terminal 2)

```
convo Andrew Ng
```

Six months from now, I forget what I discussed with someone. No problem. I ask the agent and it pulls the full email conversation from Inkbox — every message I sent and received with the complete body. My networking memory never fades.

---

## STEP 7 — CLOSE (show dashboard tabs: Live Feed → Network Graph → Contacts)

Everything runs through this live dashboard — real-time activity feed showing every agent action as it happens, an interactive network graph visualizing my entire professional network, and contact cards with warmth scores and outreach timelines. Email, vault, phone — all three Inkbox capabilities working together as a complete AI networking brain. That's ConNET.
