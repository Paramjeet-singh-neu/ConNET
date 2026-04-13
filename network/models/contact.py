import json
import uuid
from datetime import datetime, date, timedelta


def create_contact(
    name: str,
    email: str = "",
    company: str = "",
    role: str = "",
    venue: str = "",
    date_met: str = "",
    context_notes: str = "",
    source: str = "outbound",
    warmth_score: str = "warm",
    tags: list[str] | None = None,
) -> dict:
    now = datetime.utcnow().isoformat()
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "company": company,
        "role": role,
        "venue": venue,
        "date_met": date_met or date.today().isoformat(),
        "context_notes": context_notes,
        "source": source,
        "warmth_score": warmth_score,
        "outreach_history": [],
        "follow_up_count": 0,
        "max_follow_ups": 3,
        "next_follow_up": None,
        "tags": tags or [],
        "created_at": now,
        "updated_at": now,
    }


def contact_to_json(contact: dict) -> str:
    return json.dumps(contact)


def contact_from_json(data: str | dict) -> dict:
    if isinstance(data, str):
        return json.loads(data)
    return data


def should_follow_up(contact: dict) -> bool:
    if contact["follow_up_count"] >= contact["max_follow_ups"]:
        return False
    nfu = contact.get("next_follow_up")
    if not nfu:
        return False
    return date.fromisoformat(nfu) <= date.today()


def days_since_last_contact(contact: dict) -> int:
    history = contact.get("outreach_history", [])
    if not history:
        return 9999
    last_date = history[-1].get("date", contact["date_met"])
    try:
        last = date.fromisoformat(last_date)
        return (date.today() - last).days
    except (ValueError, TypeError):
        return 9999


def calculate_next_followup(wait_days: int) -> str:
    return (date.today() + timedelta(days=wait_days)).isoformat()
