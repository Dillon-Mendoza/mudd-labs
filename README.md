# Mudd Labs

Personal dev lab and build environment for tools I actually use.

Tools are deployed and tested across a self-managed Tailscale mesh of Linux devices; not just written and pushed

---

## What's here

**[`clearmudd/`](./clearmudd/)** - SSH audit and access intelligence tool. Parses auth logs, surfaces failed attempts, accepted keys, and session patterns. Built to run on any node in the mesh.

**[`mudd/`](./mudd)** — CLI session journaling tool. Project-scoped, terminal-native. Logs what I built, what broke, and what I learned; tied to the working directory.
 
**[`dashboard/`](./dashboard)** — Homelab visibility layer. Pulls live metrics from Netdata across devices and surfaces them in a single view.
 
---

## Status

| Project | Status | Updated |
|---|---|---|
| `clearmudd` | Active development — parser complete, expanding features | 2026 June 4th |
| `mudd` | Specced, build not started | 2026 June 4th |
| `dashboard` | Early stage — Django app running, not yet configured | 2026 June 4th |

---


## Stack
 
Python · Bash · Linux (Fedora, Ubuntu) · Tailscale · systemd · Docker · Git
 
---
 
## Background
 
Self-taught. Nine years in hospitality, now building toward Linux administration and Python development. The homelab is the resume; documented infrastructure, real deployment, things that break and get fixed.
 
