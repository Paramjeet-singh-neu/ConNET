# Vendored Inkbox sample client/server

This directory is a snapshot of [inkbox-ai/sample-client-server](https://github.com/inkbox-ai/sample-client-server).

ConNET-specific change: `src/server.py` invokes `connet_webhook_hook.on_inkbox_webhook` when the environment variable `CONNET_WEBHOOK_INTEGRATION` is true (set automatically by `network/run_inkbox_gateway.py`).

To refresh from upstream, replace this tree and re-apply the small hook block in `server.py` after the `_parse_webhook` call (search for `CONNET_WEBHOOK_INTEGRATION`).
