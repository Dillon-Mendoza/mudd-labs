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

