OUTREACH_EMAIL_PROMPT = """Write a cold outreach email from Paramjeet, an AI/ML Engineer.

Research on target: {research_json}

Rules:
- Body MUST be under 300 characters
- Reference ONE specific thing about them
- Connect to ONE specific thing about Paramjeet (CoachMe+ win, RAG expertise, boxing, Northeastern)
- End with a soft call-to-action question
- Tone: warm, confident, conversational — NOT salesy or formal
- No "I'd love to pick your brain" or similar cliches

Paramjeet's highlights:
- Built CoachMe+ (AI sports coaching plugin) — won grand prize at Voxel51 hackathon
- 3+ years building LLM pipelines, RAG systems, agentic AI in production
- MS graduating from Northeastern April 2026
- Self-taught boxer

Return JSON: {{"subject": "...", "body": "...", "angle_used": "..."}}"""
