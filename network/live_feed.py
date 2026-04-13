"""Live activity feed — tracks all agent events for real-time dashboard streaming."""

import json
import time
import threading
from collections import deque
from datetime import datetime


class LiveFeed:
    """Thread-safe event queue for Server-Sent Events (SSE) streaming to dashboard."""

    def __init__(self, max_events: int = 100):
        self._events = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._subscribers: list = []

    def push(self, event_type: str, data: dict):
        """Push an event to the feed."""
        event = {
            "id": len(self._events),
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        with self._lock:
            self._events.append(event)
        # Notify subscribers
        for q in self._subscribers:
            q.append(event)

    def subscribe(self):
        """Return a subscriber queue that receives new events."""
        q = deque()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q):
        """Remove a subscriber queue."""
        try:
            self._subscribers.remove(q)
        except ValueError:
            pass

    def recent(self, n: int = 20) -> list[dict]:
        """Get the N most recent events."""
        with self._lock:
            return list(self._events)[-n:]

    # Convenience methods for common event types

    def log_outbound(self, name: str, company: str, subject: str, angle: str):
        self.push("outbound", {
            "icon": "🚀",
            "title": f"Outreach sent to {name}",
            "detail": f"at {company} — \"{subject}\"",
            "meta": angle,
        })

    def log_inbound(self, sender: str, classification: str, priority: str, summary: str):
        self.push("inbound", {
            "icon": "📨",
            "title": f"Inbound from {sender}",
            "detail": f"Classified: {classification} | Priority: {priority}",
            "meta": summary,
        })

    def log_reply_sent(self, to: str, classification: str):
        self.push("reply", {
            "icon": "💬",
            "title": f"Smart reply sent to {to}",
            "detail": f"Based on {classification} classification",
            "meta": "",
        })

    def log_sentiment(self, contact: str, warmth: str, scores: dict):
        self.push("sentiment", {
            "icon": "🎯",
            "title": f"Sentiment scored: {contact}",
            "detail": f"Warmth: {warmth} (E:{scores.get('enthusiasm',0)} S:{scores.get('specificity',0)} N:{scores.get('next_step_signal',0)})",
            "meta": scores.get("follow_up_strategy", ""),
        })

    def log_followup(self, name: str, attempt: int, subject: str):
        self.push("followup", {
            "icon": "🔄",
            "title": f"Follow-up #{attempt} to {name}",
            "detail": subject,
            "meta": "",
        })

    def log_agent_comms(self, agent_a: str, agent_b: str, reason: str):
        self.push("agent_comms", {
            "icon": "🤖",
            "title": f"Agent handshake: {agent_a} ↔ {agent_b}",
            "detail": reason,
            "meta": "",
        })

    def log_briefing(self, method: str, script: str):
        self.push("briefing", {
            "icon": "📞",
            "title": f"Briefing sent via {method}",
            "detail": script[:100] + "..." if len(script) > 100 else script,
            "meta": "",
        })

    def log_vault_store(self, name: str, source: str, warmth: str):
        self.push("vault", {
            "icon": "🔐",
            "title": f"Stored: {name}",
            "detail": f"Source: {source} | Warmth: {warmth}",
            "meta": "",
        })

    def log_intro(self, person_a: str, person_b: str, reason: str):
        self.push("intro", {
            "icon": "🤝",
            "title": f"Smart intro: {person_a} ↔ {person_b}",
            "detail": reason,
            "meta": "",
        })


# Global singleton
feed = LiveFeed()
