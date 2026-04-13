"""Flask API for the React dashboard — with SSE live feed and network graph data."""

import json
import time
from flask import Flask, jsonify, send_from_directory, request, Response
from flask_cors import CORS
from inkbox import Inkbox

from config import INKBOX_API_KEY, VAULT_KEY
from memory import VaultManager
from live_feed import feed

app = Flask(__name__, static_folder="dashboard")
CORS(app)

_inkbox = None
_vault = None


def get_vault():
    global _inkbox, _vault
    if _vault is None:
        _inkbox = Inkbox(api_key=INKBOX_API_KEY)
        _inkbox.__enter__()
        _vault = VaultManager(_inkbox, VAULT_KEY)
    return _vault


@app.route("/")
def index():
    return send_from_directory("dashboard", "index.html")


@app.route("/api/contacts")
def get_contacts():
    vault = get_vault()
    return jsonify(vault.get_all_contacts())


@app.route("/api/contacts/<email>")
def get_contact(email):
    vault = get_vault()
    contact = vault.get_contact(email)
    if contact is None:
        return jsonify({"error": "Contact not found"}), 404
    return jsonify(contact)


@app.route("/api/contacts/search")
def search_contacts():
    query = request.args.get("q", "")
    vault = get_vault()
    if not query:
        return jsonify([])
    return jsonify(vault.search_contacts(query))


@app.route("/api/stats")
def get_stats():
    vault = get_vault()
    contacts = vault.get_all_contacts()
    return jsonify({
        "total": len(contacts),
        "hot": len([c for c in contacts if c.get("warmth_score") == "hot"]),
        "warm": len([c for c in contacts if c.get("warmth_score") == "warm"]),
        "cold": len([c for c in contacts if c.get("warmth_score") == "cold"]),
        "pending_followups": len(vault.get_stale_contacts()),
        "sources": {
            "inbound": len([c for c in contacts if c.get("source") == "inbound"]),
            "outbound": len([c for c in contacts if c.get("source") == "outbound"]),
            "agent": len([c for c in contacts if c.get("source") == "agent"]),
        },
    })


@app.route("/api/graph")
def get_graph():
    """Return nodes and edges for the D3 force-directed network graph."""
    vault = get_vault()
    contacts = vault.get_all_contacts()

    nodes = [{"id": "paramjeet", "name": "Paramjeet", "group": "self", "warmth": "self"}]
    edges = []

    for c in contacts:
        node_id = c.get("email", c["id"])
        nodes.append({
            "id": node_id,
            "name": c["name"],
            "company": c.get("company", ""),
            "group": c.get("source", "outbound"),
            "warmth": c.get("warmth_score", "warm"),
        })
        edges.append({"source": "paramjeet", "target": node_id, "type": c.get("source", "outbound")})

    # Add edges between contacts that share a company or venue
    for i, a in enumerate(contacts):
        for b in contacts[i + 1:]:
            if a.get("company") and a.get("company") == b.get("company"):
                edges.append({"source": a.get("email", a["id"]), "target": b.get("email", b["id"]), "type": "company"})
            elif a.get("venue") and a.get("venue") == b.get("venue"):
                edges.append({"source": a.get("email", a["id"]), "target": b.get("email", b["id"]), "type": "venue"})

    return jsonify({"nodes": nodes, "edges": edges})


@app.route("/api/feed")
def get_feed():
    """Return recent activity feed events."""
    n = request.args.get("n", 20, type=int)
    return jsonify(feed.recent(n))


@app.route("/api/feed/stream")
def stream_feed():
    """SSE endpoint — streams live events to the dashboard."""
    def generate():
        q = feed.subscribe()
        try:
            while True:
                if q:
                    event = q.popleft()
                    yield f"data: {json.dumps(event)}\n\n"
                else:
                    time.sleep(0.5)
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            feed.unsubscribe(q)

    return Response(generate(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })


if __name__ == "__main__":
    print("Starting NetWork Dashboard API on http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=True, threaded=True)
