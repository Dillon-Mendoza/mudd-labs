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

The `mudd commit` interaction is modeled after `git commit -m""`. It's not a 