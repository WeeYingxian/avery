"""Local server for the Avery Plan tracker.

Serves the page and keeps one shared copy of your choices in plan-state.json,
so anything ticked on one device shows up on the other. Bind to your Wi-Fi so
both of you can reach it:

    python server.py            # shared over Wi-Fi on port 4173
    python server.py --local    # this computer only
    python server.py --port 8080

Anyone on the same Wi-Fi who has the address can read and edit the plan. There
is no password. Run it on a home network, not a cafe one.
"""

import argparse
import json
import socket
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
STATE_FILE = HERE / "plan-state.json"
SNAPSHOT_FILE = HERE / "initial-plan.json"
PAGE = HERE / "index.html"
KEYS = ("settings", "tasks", "buys", "checks")

_lock = threading.Lock()


def blank_state():
    return {"rev": 0, **{k: {} for k in KEYS}}


def seeded_state():
    """What this computer starts from when it has no answers of its own.

    The page seeds an empty browser from initial-plan.json, which is how the
    website opens on the published answers instead of a blank plan. Do the
    same here, or the two copies disagree: the website shows the decisions and
    the one at home looks like nothing was ever discussed.

    Only a *missing* file seeds. Clearing your answers in the app writes an
    empty file, and an empty file stays empty rather than refilling itself.
    """
    state = blank_state()
    try:
        snapshot = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return state
    if not isinstance(snapshot, dict):
        return state
    for key in KEYS:
        value = snapshot.get(key)
        if isinstance(value, dict):
            state[key] = value
    return state


def load_state():
    if not STATE_FILE.exists():
        return seeded_state()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return blank_state()
    data.setdefault("rev", 0)
    for k in KEYS:
        if not isinstance(data.get(k), dict):
            data[k] = {}
    return data


def merge_state(incoming):
    """Merge one client's changes in, two levels deep.

    Two levels is what the page's own shape needs: tasks/buys/checks are keyed
    by item id, and each value is a small object. Merging per field rather than
    replacing whole documents means two people editing different tasks at the
    same time do not overwrite each other.
    """
    with _lock:
        state = load_state()
        for key in KEYS:
            patch = incoming.get(key)
            if not isinstance(patch, dict):
                continue
            target = state[key]
            for field, value in patch.items():
                if isinstance(value, dict) and isinstance(target.get(field), dict):
                    target[field] = {**target[field], **value}
                else:
                    target[field] = value
        state["rev"] = int(state.get("rev", 0)) + 1
        tmp = STATE_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, indent=1), encoding="utf-8")
        tmp.replace(STATE_FILE)
        return state


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return None


class Handler(BaseHTTPRequestHandler):
    server_version = "AveryPlan/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        if self.path.startswith("/api/state") and self.command == "GET":
            return  # the page polls this; do not fill the console with it
        super().log_message(fmt, *args)

    def _send(self, code, body, ctype):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json; charset=utf-8")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            if not PAGE.exists():
                return self._send(500, "index.html is missing. Run: python build-local.py", "text/plain")
            return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if path in ("/favicon.ico", "/avery.ico"):
            icon = HERE / "avery.ico"
            if icon.exists():
                return self._send(200, icon.read_bytes(), "image/x-icon")
            return self._send(404, "No icon", "text/plain")
        if path == "/api/state":
            return self._json(200, load_state())
        if path == "/api/net":
            return self._json(200, {
                "urls": self.server.share_urls,
                "shared": self.server.shared,
                "stateFile": str(STATE_FILE.resolve()),
                "folder": str(HERE.resolve()),
            })
        self._send(404, "Not found", "text/plain")

    def do_POST(self):
        if self.path.split("?")[0] != "/api/state":
            return self._send(404, "Not found", "text/plain")
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > 4_000_000:
                return self._json(413, {"error": "too large"})
            incoming = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(incoming, dict):
                raise ValueError("expected an object")
        except (ValueError, OSError) as exc:
            return self._json(400, {"error": str(exc)})
        return self._json(200, merge_state(incoming))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=4173)
    ap.add_argument("--local", action="store_true", help="this computer only, no Wi-Fi sharing")
    ap.add_argument("--open", action="store_true", help="open the page in your browser once running")
    args = ap.parse_args()

    host = "127.0.0.1" if args.local else "0.0.0.0"
    ip = None if args.local else lan_ip()
    urls = [f"http://{ip}:{args.port}/"] if ip else []
    home = f"http://localhost:{args.port}/"

    try:
        httpd = ThreadingHTTPServer((host, args.port), Handler)
    except OSError as exc:
        if getattr(exc, "errno", None) in (48, 98, 10048):
            print(f"Already running. Opening {home}")
            if args.open:
                webbrowser.open(home)
            return 0
        raise
    httpd.share_urls = urls
    httpd.shared = not args.local

    print(f"Avery Plan  ->  {home}")
    if urls:
        print(f"On your Wi-Fi ->  {urls[0]}")
        print("Anyone on this network with that address can read and edit the plan.")
    else:
        print("Local only. Drop --local to share over Wi-Fi.")
    if STATE_FILE.exists():
        print(f"Shared state: {STATE_FILE.name}")
    else:
        print(f"Shared state: {STATE_FILE.name} (starting from {SNAPSHOT_FILE.name}, "
              f"the same answers the website shows)")
    print("Keep this window open. Close it, or press Ctrl+C, to stop sharing.")

    if args.open:
        threading.Timer(0.6, webbrowser.open, args=(home,)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
