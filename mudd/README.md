# mudd - Session Journaling CLI
### Mudd Labs | Project Spec v0.2

---

## What Is It

`mudd` is a personal session journaling CLI that lives inside individual projects repositories. It captures the full story of a work session; every command that was ran passively, every decision annotated intentionally. Writes it to a structured log file that the developer can open and review when it's time to write real documentation

Git tracks *what changed*. `mudd` tracks *why it changed.*

---

## The Problem It Solved

Deep work fills proper documentation. When you're in flow: breaking things, googling, fixing, iterating. The reasoning behind decision evaporates. By the time you surface, you remember what you built but not why you built it that way. The result is runbooks and READMEs that describe *what* but never the *why*, and onboarding that requires a conversation instead of a document

`mudd` captures that layer in real time, at the moment the thought exists, without interrupting the work

--

## Core Concept

Two event types. One log file.

- **CMD** - every command ran during an active session, captured passively by the recorder
- **COMMIT** - an intentional annotation made by the developer at a moment of choise

The `mudd commit` interaction is modeled after `git commit -m""`. It's not a note it's a checkpoint.

`mudd` is a **reference layer**,  not a documentation layer. It captures the session faithfully so that when you sit down to write the actual runbook or README.m, you  ave accurate raw material to work from instead of reconstructed memory. The documentation still gets written by you, intentionally, in the right place. `mudd` makes sure the material exists when you need it.

---

## Design Philosophy

### Project Scoped, always
`mudd` is inspired by git's model. You opt in per repo with `mudd init`. Everything lives in in `.mudd/` at the repo root. If `.mudd/` doesn't exist, `mudd` doesn't operate; no silent global fallback, no assumption about your machine. The developer owns exactly what gets logged, where it lives, and what stays private.

### Logs are just files
Session logs are plain readable files. The developer should be able to `vim` or `nano` directly int `.mudd/sessions/<repo-name>.log` and read it without any special command. No proprietary format, no tool required to access your own data.

### Privacy by default
`.mudd/` is added to `.gitignore` automatically on `mudd init`. Session log captures stay on your machine unless you explicitly choose otherwise.

### Reference, not replacement
`mudd` does not auto-generate documentation. It does not summarize sessions. it does not push to Confluence or any external system. It exists between "I was deep in work" and "I need to write this up", bridging the gap so the write up is accurate. The deliberate act of writing documentation remains yours.

---

## Directory Structure

```
your-repo/
|-- .gitignore      #.mudd/ added here automatically on init
|-- .mudd/
|   |--config       # project level mudd settings
|   |--sessions/
|       |--<example-logbook>
|       |--<example-logbook2>
|--src/
|--README.md
```

Session logs are flat filed. Human readable without the tool and openable with any editor.

---

## CLI Interface

### Initialize mudd in a repo
```bash
mudd init
```
Creates `.mudd/` directory structure in the current repo. Adds `.mudd/` to `.gitignore`. One time setup per project.

### Start a new session
```bash
mudd activate -sn <session_name>
```
Creates a new named session log under `.mudd/sessions/`, starts passive command recording.

### Resume an existing session
```bash
mudd activate -ssid <session_name>
```
Reopens the named session log and continues appending. Same file, continuous record.

### Annotate a decision
```bash
mudd commit "Chose Tailscale over Wireguard directly, easier ACL management and no exposed ports."
```
Writes a timestamped COMMIT entry to the active session log. This is the human layer, capture the thought at the commit it exists.

### End a session
```bash
mudd deactivate
```
Closes the active session, writes SESSION END marker to the log.

### View a session
```bash
mudd log <session-name>
mudd log <session-name> --timestamp=enabled
```
Renders the session log to terminal. Color coded: CMD in one tone, COMMIT in another. Timestamps of by default, enabled with flag

---

## Data Model

Every entry is stored with full metadata regardless of display settings/ Storage is the source of truth. Display is a view layer on top. This means future features like filtering searching, or custom exports never require re-engineering the storage layer.

### Stored format (always)
``` 
timestamp=2026-05-29T14:32:01 | type=SESSION_START | session=dashboard_logbook
timestamp=2026-05-29T14:32:04 | type=CMD | value=ssh tp-mudd@dell-server
timestamp=2026-05-29T14:32:09 | type=CMD | value=cd /opt/n8n
timestamp=2026-05-29T14:32:15 | type=CMD | value=docker ps
timestamp=2026-05-29T14:33:01 | type=COMMIT | value=containers were down after reboot — docker wasn't set to restart:always, fixing now
timestamp=2026-05-29T14:33:12 | type=CMD | value=docker update --restart=always n8n
timestamp=2026-05-29T14:34:00 | type=SESSION_END | session=dashboard_logbook
```

### Default display (timestamps off)
```
SESSION START - dashboard_logbook

CMD     ssh tp-mudd@dell-server
CMD     cd /opt/n8n
CMD     docker ps
COMMIT  containers were down after reboot; docker wasn't set to restart:always, fixing now
CMD     docker update --restart=always n8n

SESSION END
```

### Display with --timestamp=enabled
```
SESSION START - dashboard_logbook [2026-05-29 14:32:01]

CMD     [14:32:04]  ssh tp-mudd@dell-server
CMD     [14:32:09]  cd /opt/n8n
CMD     [14:32:15]  docker ps
COMMIT  [14:33:01]  containers were down after reboot — docker wasn't set to restart:always, fixing now
CMD     [14:33:12]  docker update --restart=always n8n
 
SESSION END  [14:34:00]
```

---

## What mudd Is Not

- Not a replacement for git or version control
- Not a team tool; project scoped, lives on individual machines, serves the individual developer
- Not a documentation generator; it does not write your runbooks or READMEs for you
- Not a knowledge base or search system
- Not a deployment or audit tool
- Nothing changes at the production or team collaboration level

---

## Build Phases

### Phase 1 - Core loop
- `mudd init` — create `.mudd/` structure, update `.gitignore`
- `mudd activate -sn <name>` — create session, start passive recorder, open log
- `mudd commit "<message>"` — write COMMIT entry to active session log
- `mudd activate -ssid <name>` — resume named session, continue appending
- `mudd deactivate` — close session, write SESSION END
- All metadata stored. Raw output. No display polish yet.
- **Goal: confirm the core loop works end to end**
### Phase 2 — Display layer
- `mudd log <name>` — render session to terminal
- Color-coded CMD vs COMMIT output
- `--timestamp=enabled` flag
- **Goal: make the output actually readable**
### Phase 3 — UX hardening
- Edge cases: interrupted sessions, crash recovery, missing SESSION_END
- `mudd sessions` — list all named sessions in current repo
- Session naming rules — enforce slug format, handle edge cases
- **Goal: tool is reliable enough for daily use**
---
 
## Tech Stack
 
- **Language:** Python
- **Storage:** Flat log files, one per session, stored in `.mudd/sessions/`
- **Passive recorder:** Shell hook — `PROMPT_COMMAND` for Bash (Phase 1 target), shell-agnostic expansion in later phases
- **Scope:** Project-local CLI, initialized per repo
---
 
## Open Questions
 
1. Passive command capture implementation — `PROMPT_COMMAND` hook confirmed for Bash. How does `mudd` inject/remove the hook cleanly on `activate`/`deactivate` without polluting the developer's shell config permanently?
2. What happens on interrupted sessions (crash, lost connection)? Does SESSION_END get written? Is there a recovery path on next `mudd activate -ssid`?
3. Session naming — enforce slug format (no spaces) at `activate` time or handle gracefully?
4. Config file contents — what lives in `.mudd/config`? Shell preference? Display defaults? Color scheme?
5. Multi-device: sessions are local and private by design. Is there ever a case for the developer to manually push `.mudd/` to a private branch? Out of scope for now but worth holding.
---
 
## Relationship to ClearMudd
 
Not defined yet. ClearMudd is SSH audit and access intelligence. `mudd` captures annotated command history with developer reasoning. There is an obvious surface area overlap — a tool that logs *what commands ran* and a tool that logs *why those commands ran* are naturally adjacent. The connection may become architectural once both tools exist. Do not force it. Build `mudd` standalone and let the relationship reveal itself.
 
---
 
 
*Spec compiled: 2026-05-29 | Version: 0.2 | Status: Pre-build | Next action: Phase 1 implementation*
