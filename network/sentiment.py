"""Sentiment analysis on email replies — scores enthusiasm, specificity, next-step signals."""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from models.contact import calculate_next_followup
from prompts.sentiment_score import SENTIMENT_PROMPT
from live_feed import feed


def _parse_llm_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


class SentimentAnalyzer:
    def __init__(self, llm: ChatOpenAI, vault_manager):
        self.llm = llm
        self.vault = vault_manager

    async def analyze_reply(self, original_subject: str, sender: str, reply_body: str) -> dict:
        """Score sentiment and update vault."""
        # Step 1: Run sentiment prompt
        scores = await self._score(original_subject, sender, reply_body)

        # Step 2: Update vault with warmth score
        self.vault.update_warmth(sender, scores["warmth"])

        # Step 3: Update follow-up schedule
        wait_days = scores.get("suggested_wait_days", 7)
        self.vault.update_contact(sender, {
            "next_follow_up": calculate_next_followup(wait_days),
            "warmth_score": scores["warmth"],
        })

        feed.log_sentiment(sender, scores["warmth"], scores)

        print(f"    Sentiment: {scores['warmth']} (enthusiasm={scores['enthusiasm']}, specificity={scores['specificity']}, next_step={scores['next_step_signal']})")
        return scores

    async def _score(self, original_subject: str, sender: str, reply_body: str) -> dict:
        """Run sentiment analysis LLM chain."""
        prompt = SENTIMENT_PROMPT.format(
            original_subject=original_subject,
            sender=sender,
            reply_body=reply_body,
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return _parse_llm_json(response.content)
        except json.JSONDecodeError:
            return {
                "enthusiasm": 5,
                "specificity": 5,
                "next_step_signal": 5,
                "warmth": "warm",
                "follow_up_strategy": "Send a value-add follow-up in a week",
                "suggested_wait_days": 7,
            }
