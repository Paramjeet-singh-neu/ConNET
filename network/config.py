import os
from dotenv import load_dotenv

load_dotenv()

INKBOX_API_KEY = os.getenv("INKBOX_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MY_EMAIL = os.getenv("MY_EMAIL", "i.am.paramjeet31@gmail.com")
MY_PHONE = os.getenv("MY_PHONE", "+13034756390")
VAULT_KEY = os.getenv("VAULT_KEY", "ConNET-Vault-2026!")
AGENT_NAME = os.getenv("AGENT_NAME", "paramjeet-agent")
AGENT2_NAME = os.getenv("AGENT2_NAME", "testAgent")
INKBOX_API_KEY_2 = os.getenv("INKBOX_API_KEY_2")
OPENAI_MODEL = "gpt-4o"
MAX_FOLLOW_UPS = 3
FOLLOW_UP_DAYS = 7

# Inkbox org Contacts + Notes (SDK 0.3+)
CONNET_ORG_CONTEXT = os.getenv("CONNET_ORG_CONTEXT", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
CONNET_AUTO_NOTE_HOT_INBOUND = os.getenv(
    "CONNET_AUTO_NOTE_HOT_INBOUND", "false",
).strip().lower() in {"1", "true", "yes", "on"}
