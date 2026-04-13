FOLLOWUP_PROMPT = """Draft a follow-up email for an unresponsive contact.

Contact: {contact_json}
Original email: {original_email}
Days elapsed: {days_elapsed}
Attempt: {attempt_number} of 3
Warmth: {warmth}

Warmth rules:
- hot: Direct, reference something new
- warm: Add value, share relevant project/article
- cold: Final attempt, short, no pressure. "No worries if the timing isn't right."

Fresh research (new info since last email): {fresh_research}

Body MUST be under 200 characters. Reply in same thread.

Return JSON: {{"subject": "Re: ...", "body": "...", "fresh_angle": "what new info was used"}}"""
