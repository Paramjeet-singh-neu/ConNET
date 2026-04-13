SENTIMENT_PROMPT = """Analyze the sentiment of this email reply.

Original outreach: {original_subject}
Reply from: {sender}
Reply: {reply_body}

Score 1-10:
1. "enthusiasm" (1=dismissive, 10=excited)
2. "specificity" (1=generic, 10=detailed)
3. "next_step_signal" (1=closing conversation, 10=wants to meet)

Classify overall warmth:
- "hot": avg >= 7 — follow up quickly, be direct
- "warm": avg 4-6 — follow up in a week, add value
- "cold": avg <= 3 — one more try max, then park

Determine follow-up strategy:
- "hot": schedule a call, be direct about intent
- "warm": share something relevant, keep conversation going
- "cold": one final value-add email, then wait 3 months

Return JSON: {{"enthusiasm": 0, "specificity": 0, "next_step_signal": 0, "warmth": "hot|warm|cold", "follow_up_strategy": "description", "suggested_wait_days": 7}}"""
