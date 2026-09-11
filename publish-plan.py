"""Copy your current answers into the snapshot the website serves.

GitHub Pages has no server behind it. It seeds a browser from
initial-plan.json, which is committed, so the website keeps showing whatever
was published last. Run this after a round of decisions, then commit and push,
and the website says the same things as the copy at home.

    python publish-plan.py

Nothing is sent anywhere by this script. It writes one file; you still choose
whether to commit it. Bear in mind what that commit means: the snapshot ships
with the site, so every answer in it, free-text notes included, becomes
readable by anyone who opens the page.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
STATE_FILE = HERE / "plan-state.json"
SNAPSHOT_FILE = HERE / "initial-plan.json"
KEYS = ("settings", "tasks", "buys", "checks")


def read(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return None
    except ValueError as exc:
        print(f"{path.name} is not readable JSON: {exc}")
        raise SystemExit(1)
    return data if isinstance(data, dict) else None


def main():
    state = read(STATE_FILE)
    if state is None:
        print(f"No answers to publish: {STATE_FILE.name} is missing.")
        return 1

    published = read(SNAPSHOT_FILE) or {}
    snapshot = {
        "app": "Avery Plan",
        "savedAt": datetime.now(timezone.utc).isoformat(),
    }
    for key in KEYS:
        value = state.get(key)
        snapshot[key] = value if isinstance(value, dict) else {}

    changed = [k for k in KEYS if snapshot[k] != published.get(k)]
    if not changed:
        print("The website already shows these answers. Nothing to publish.")
        return 0

    for key in changed:
        before = len(published.get(key) or {})
        after = len(snapshot[key])
        print(f"  {key}: {before} -> {after} entries")

    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {SNAPSHOT_FILE.name}. To put it on the website:")
    print(f'  git add {SNAPSHOT_FILE.name} && git commit -m "Publish current answers" && git push')
    return 0


if __name__ == "__main__":
    sys.exit(main())
