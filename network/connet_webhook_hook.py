"""
ConNET hooks for the vendored Inkbox sample gateway (POST /webhook).

When CONNET_WEBHOOK_INTEGRATION is enabled, vendor server.py calls
``on_inkbox_webhook`` after signature verification and parsing.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from live_feed import feed

logger = logging.getLogger("connet_webhook")

_agent = None
_init_lock = asyncio.Lock()


async def _get_agent():
    global _agent
    async with _init_lock:
        if _agent is None:
            from agent_core import NetworkAgent

            _agent = NetworkAgent()
        return _agent


async def on_inkbox_webhook(payload: Any) -> None:
    from data_models.webhooks import (
        MailWebhookEventType,
        MailWebhookPayload,
        MessageDirection,
        PhoneIncomingCallWebhookPayload,
        PhoneIncomingTextWebhookPayload,
    )

    if isinstance(payload, MailWebhookPayload):
        await _handle_mail(payload)
    elif isinstance(payload, PhoneIncomingTextWebhookPayload):
        await _handle_sms(payload)
    elif isinstance(payload, PhoneIncomingCallWebhookPayload):
        logger.info(
            "ConNET: incoming call webhook id=%s status=%s from=%s",
            payload.id,
            payload.status.value,
            payload.remote_phone_number,
        )


async def _handle_mail(payload: MailWebhookPayload) -> None:
    from data_models.webhooks import MailWebhookEventType, MessageDirection

    if payload.event_type != MailWebhookEventType.MESSAGE_RECEIVED:
        return
    msg = payload.data.message
    if msg.direction != MessageDirection.INBOUND:
        return

    agent = await _get_agent()
    detail = agent.identity.get_message(str(msg.id))
    body = (detail.body_text or detail.body_html or "").strip()
    if not body:
        body = (msg.snippet or "").strip()

    email_data = {
        "id": str(msg.id),
        "from": msg.from_address,
        "to": msg.to_addresses,
        "subject": msg.subject or "(no subject)",
        "body": body,
        "thread_id": str(msg.thread_id) if msg.thread_id else None,
        "message_id": msg.message_id,
        "direction": str(msg.direction.value),
    }

    await agent.inbound.process_email(email_data)
    try:
        agent.identity.mark_emails_read([str(msg.id)])
    except Exception as e:
        logger.warning("Could not mark message read: %s", e)

    agent.activity["inbound_count"] = agent.activity.get("inbound_count", 0) + 1


async def _handle_sms(payload: PhoneIncomingTextWebhookPayload) -> None:
    t = payload.data.text_message
    feed.push(
        "sms",
        {
            "icon": "📱",
            "title": f"SMS from {t.remote_phone_number}",
            "detail": (t.text or "")[:200],
            "meta": t.local_phone_number,
        },
    )
    logger.info(
        "ConNET: inbound SMS from=%s to=%s",
        t.remote_phone_number,
        t.local_phone_number,
    )
