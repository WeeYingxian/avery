# Avery Plan

A private planning tracker for a first baby in Singapore — costs, government
support, a task list by stage, and a board for the decisions the two of you
need to make together.

Everything you both tick, pick or write is shared. Nothing is sent anywhere
except between your own devices and, if you use the published link, your
Claude account.

---

## Opening it

**Double-click "Avery Plan" on the desktop.** That starts a small server on
this computer and opens the page. A console window appears and **must stay
open** — closing it stops the server and stops Wi-Fi sharing.

| Where | Address |
|---|---|
| This computer | http://localhost:4173 |
| Anyone on your Wi-Fi | Use the **Share & storage** button in the page header |
| From anywhere | https://claude.ai/code/artifact/e5010090-aec9-474e-a239-d172817c2bec |

The Wi-Fi address changes when your router reassigns it, which is why the
Share button reads it live instead of hard-coding it. Don't write it down.

There is also a Start Menu entry, and you can pin either to the taskbar
(right-click → Show more options → Pin to taskbar).

---

## Where your answers are saved

```
plan-state.json
```

One plain text file in this folder. You can open it in Notepad. Both of you
write to the same file, which is what makes the Wi-Fi sharing actually
shared rather than two separate copies.

It lives in OneDrive, so it is backed up automatically and you can right-click
→ **Version history** to recover an earlier state.

The published link on claude.ai keeps its own separate copy on Claude's
servers, so it works away from home but does not sync with this file. Pick one
as your main copy — the local one is the fuller record.

Both versions have **Back up a copy** and **Restore from a backup** under
**Share & storage** in the header.

> `plan-state.before-merge.json` is a snapshot taken before some duplicate
> cards were merged. Safe to delete whenever you like.

---

## What is in it

Five tabs where you change things, then one tab of reading.

| Tab | What it does |
|---|---|
| **Overview** | Where things stand, and the decisions that move the money most |
| **Talk it through** | One card per conversation, with what you decided |
| **Money** | The cost model. Change a setting and every total updates |
| **Tasks by stage** | Opens on what is due now: the current stage, plus anything left from earlier ones. Switch to **Everything, by stage** for the whole list or **Paperwork only** for the admin in the order it has to happen. Add your own |
| **What to buy** | 29 items, three price tiers each, feeding into Money |
| **Reference** | Grants & schemes, Public or private, Care & support, Sources. Reading only |

Two things worth knowing about how it behaves:

- **Decisions on the board drive the Money tab.** Mark a card agreed, or just
  write a decision on it, and the matching assumption updates. Change that
  setting by hand afterwards and the Money tab tells you it no longer matches
  the board, with a button to put it back.
- **Anything marked `assumed`** is a starting guess neither of you has chosen.
  Change it, or click the badge to keep the guess as your choice, and the
  badge clears.

---

## The files

| File | What it is |
|---|---|
| `avery-plan.html` | **The source.** Edit this one |
| `index.html` | Built copy the server serves. Do not edit — it gets overwritten |
| `build-local.py` | Rebuilds `index.html` from the source |
| `server.py` | The local server and the shared-state store |
| `start-avery-plan.cmd` | What the desktop shortcut runs |
| `make-icon.py` | Regenerates `avery.ico` |
| `plan-state.json` | Your answers |

After editing `avery-plan.html`:

```bash
python build-local.py
```

Then refresh the browser. To share the updated page on claude.ai as well, ask
Claude to republish it.

---

## Running it by hand

```bash
python server.py
```

Options: `--local` for this computer only, no Wi-Fi sharing. `--port 8080` to
use a different port. `--open` to launch the browser too.

---

## Sharing over Wi-Fi

Anyone on your network who has the address can read and edit the plan. There
is **no password**. Fine on a home network; do not run it on café or office
Wi-Fi. Use `--local` to turn sharing off.

Windows Firewall may ask the first time someone else connects — allow Python
on **private** networks.

---

## When something goes wrong

**"python is not recognized"** — Windows puts a Microsoft Store placeholder
ahead of the real Python on this machine. The shortcut works around it by
testing each interpreter before using one. If you hit this in a terminal, use
the full path: `%USERPROFILE%\anaconda3\python.exe`.

**The page loads but nothing saves** — the header dot tells you which mode
you are in. Green "shared over Wi-Fi" means it is writing to `plan-state.json`.
Amber "saved in this browser only" means the server is not running; open the
desktop shortcut.

**Changes are not showing up** — you may have two servers running from
different sessions, and the older one answers first. Close every console
window and open the shortcut again.

**The tab icon is missing** — browsers cache favicons hard. Ctrl+Shift+R, or
open http://localhost:4173/avery.ico once directly.

**"Address already in use"** — the server is already running. The shortcut
detects this and just opens the browser.

---

## About the numbers

Researched September 2026. Policy figures come from government sources; prices
from Singapore retailers and 2026 reviews. Anything tagged `est` is a reasoned
estimate rather than a quote — replace those with real figures as you get them
(there is a price field on every shopping row).

Several 2026 measures were announced but not fully detailed — the merged
Childcare Leave scheme, the preschool fee reductions, the extended subsidies.
Those are flagged in the app. Confirm anything you are about to act on against
the official page, which the Sources tab links to and marks as official.
