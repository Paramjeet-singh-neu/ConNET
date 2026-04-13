BRIEFING_PROMPT = """Generate a 30-second spoken briefing for a phone call to Paramjeet.

Today's activity:
- New inbound: {inbound_count}
- Outbound sent: {outbound_count}
- Replies: {replies_count}
- Hot leads: {hot_leads}
- Follow-ups: {followups_sent}
- Agent connections: {agent_connections}

Priority items: {priority_items_json}

Rules:
- Max 75 words
- Start with "Hey Paramjeet, quick networking update."
- Lead with the most important item
- End with "Want me to send details to your email?"
- Conversational tone, not robotic

Return the script as plain text (this will be sent to TTS)."""
