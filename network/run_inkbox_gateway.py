#!/usr/bin/env python3
"""
Run the Inkbox reference gateway (webhooks + phone WebSocket + tunnel) with ConNET
inbound mail integration.

Usage (from repo root or network/):

  cd network && pip install -r requirements.txt -r requirements-inkbox-gateway.txt
  export CONNET_WEBHOOK_INTEGRATION=true
  python run_inkbox_gateway.py

Requires .env in this directory with INKBOX_API_KEY, INKBOX_SIGNING_KEY,
INKBOX_TUNNEL_NAME, OPENAI_API_KEY (see .env.example and vendor README).

Upstream sample: https://github.com/inkbox-ai/sample-client-server
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    net_dir = Path(__file__).resolve().parent
    repo_root = net_dir.parent
    vendor_src = repo_root / "vendor" / "inkbox-sample-client-server" / "src"

    if not vendor_src.is_dir():
        sys.exit(
            f"Missing vendored gateway at {vendor_src}. "
            "Clone with: git clone --depth 1 https://github.com/inkbox-ai/sample-client-server.git "
            f"{repo_root / 'vendor' / 'inkbox-sample-client-server'}"
        )

    os.chdir(net_dir)
    sys.path.insert(0, str(net_dir))
    sys.path.insert(0, str(vendor_src))

    os.environ.setdefault("CONNET_WEBHOOK_INTEGRATION", "true")

    from server import main as inkbox_main

    inkbox_main()


if __name__ == "__main__":
    main()
