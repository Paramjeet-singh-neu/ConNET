import os
from inkbox import Inkbox

api_key = os.environ.get("INKBOX_API_KEY")

with Inkbox(api_key=api_key) as inkbox:
    identity = inkbox.create_identity("paramjeet-agent")
    identity.create_mailbox()
    identity.send_email(
        to=["i.am.paramjeet31@gmail.com"],
        subject="Hello from my agent",
        body_text="It works!",
    )
    print("Test email sent!")
