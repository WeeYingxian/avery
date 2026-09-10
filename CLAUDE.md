# Avery Plan

A single-file planning tracker for a couple expecting their first baby in
Singapore: costs, government support, tasks by stage, and a board for the
decisions they need to make together. No framework, no build pipeline beyond
one wrapper script.

## The one rule that matters

`avery-plan.html` is the source. `index.html` is generated from it and gets
overwritten. **Never edit `index.html` directly.** Commit the rebuilt copy
alongside the source: GitHub Pages serves it from `main` at
https://weeyingxian.github.io/avery/. Keep `.nojekyll` so Pages serves the static app.

After any change to the source:

```bash
python build-local.py
```

`build-local.py` only wraps the source in a `<!doctype>` shell so a local file
does not fall into quirks mode. The published artifact supplies its own.

## Running it

The server usually is already running on port 4173. Start it with:

```bash
python server.py
```

`--local` disables Wi-Fi sharing, `--port N` changes the port, `--open`
launches a browser. Windows has a Microsoft Store `python` stub that can win on
PATH; the real interpreter is `%USERPROFILE%\anaconda3\python.exe`.

## Do not touch the state file

`plan-state.json` holds the couple's actual answers: decisions, notes, ticks.
It is real data, not fixtures. Do not edit it, and be careful driving the UI in
a browser, because **every click writes to it**. It is gitignored, along with
`plan-state.before-merge.json`.

## Verifying changes

Use the browser regression checks described in README.md. Run them with an
isolated browser context; never test against the live plan-state.json or the
user’s browser storage. The source is still built with python build-local.py.

## Layout of the source

One file, three parts: two `<style>` blocks, the markup, then one `<script>`.

**Data first.** Top-level constants hold all content: `HOSP` (hospital bills),
`ITEMS` (29 shopping items, three tiers each), `TASKS` plus `DETAIL` and
`USUAL` (the discussion board), `PHASES` (tasks by stage), `ADMIN` (the
paperwork subset), `CSP`, `LEAVE`, `TAX`, `SRC` and friends.

**Then state.** `S` holds four keys: `settings`, `tasks`, `buys`, `checks`.
`save(key, patch)` writes through to one of three backends, chosen at startup
in `initStore()`:

- `db` — the published claude.ai artifact, via `window.claude.use("db")`
- `lan` — `server.py`, which merges two levels deep so simultaneous edits on
  two devices do not clobber each other
- `local` — `localStorage` only

**Then rendering.** One `render*` function per tab, all re-run on `emit()`.

## Things that are load-bearing

**The board drives the money through explicit choices.** Relevant cards have
Review budget choices, with a cost preview before applying. The structured
`tasks[id].money` object drives assumptions. Never interpret free-text notes
as budget instructions. Legacy saved assumptions are preserved until the
user explicitly changes them. Scenario previews never save their changes.

**Tasks are stage-aware.** `currentPhase()` derives the open stage from the due
date. Later stages fold; unticked items from passed stages surface at the top
via `leftFromEarlier()`. Counts everywhere show what is due now, not a total.

**Paperwork shares ticks with the stage list.** Items in `ADMIN` deliberately
reuse ids from `PHASES` so there is one checkbox per real job.

**Tabs.** Five working tabs then one Reference tab, defined in `TABS`.
`TAB_ALIAS` keeps old links (`#admin`, `#grants`, `#care`) working.
`go("reference/hospital")` opens a tab and scrolls to a section.

## Style

Theme tokens are declared three times: bare `:root` for light, a
`prefers-color-scheme: dark` block guarded with `:root:not([data-theme="light"])`,
and `:root[data-theme="dark"]`. Every colour comes from a token, never a
literal, or one theme breaks.

Type is Fraunces for headings and tile numbers, Figtree for everything else,
IBM Plex Mono only for the file path and Wi-Fi address. Palette is a blush-grey
ground with blueberry accent and apricot as the second hue; green, amber and
rose are reserved for meaning (agreed, assumed, over budget).

The only external dependencies are Google Fonts and the qrcode-generator
script from cdnjs. The page must keep working inside the artifact CSP, so no
other hosts and no external stylesheets beyond fonts.

## Accuracy

Policy figures are checked against government sources and cited on the
Reference tab, which marks official pages. Anything tagged `est` is a reasoned
estimate, not a quote. Before changing a number, verify it; several 2026
measures were announced without full detail and are flagged in the app.
