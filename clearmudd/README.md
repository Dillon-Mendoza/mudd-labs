# ClearMudd

> SSH audit log parser and access intelligence tool.  
> Built on real infrastructure. Owned end to end.

---

## What It Does

ClearMudd parses SSH authentication logs from `journalctl` output, extracts structured access data, detects anomalous patterns, and notifies the system owner via Discord.

This is not a tutorial project. It is built against a real homelab running Fedora and Ubuntu servers, hardened with FirewallD and UFW, confined to a Tailscale mesh network. Every pattern in this codebase was derived from real log output on real machines.

---

## Why It Exists

Standard log monitoring tools exist. ClearMudd exists because building it requires understanding SSH authentication deeply — how sessions are established, what a brute force attempt looks like versus a fumbled password, how PAM layers on top of sshd, and how to extract signal from unstructured text programmatically.

It is a portfolio project in the truest sense: the learning is the point, and the output is real.

---

## Target Fields

Each SSH log event is parsed for the following fields:

| Field | Source | Description |
|-------|--------|-------------|
| `session_id` | `sshd-session[N]` | Correlation key — joins accept/open/close lines |
| `hostname` | Field 4 of log line | Device the event occurred on |
| `timestamp` | Fields 1-3 | When the event occurred |
| `outcome` | `Accepted` / `Failed` / `Invalid` | Result of the auth attempt |
| `auth_method` | `password` / `publickey` | How authentication was attempted |
| `username` | `for <user>` | Account targeted |
| `uid` | `uid=N` | System UID of authenticated user |
| `source_ip` | `from <ip>` | Origin of the connection attempt |

---

## Detection Logic

### Brute Force Signal
- Same source IP
- Multiple `Failed` or `Invalid` events
- No `Accepted` event
- Volume of failures over time from a single IP

### Line Type Routing
SSH logs contain multiple line types per session. ClearMudd identifies line type before parsing:

- `Accepted` / `Failed` / `Invalid` lines → outcome, auth method, username, IP, session ID
- `pam_unix(sshd:session): session opened` lines → UID correlation
- All other lines → ignored

This is intentional. Parsing every field from every line is both incorrect and inefficient. Line type routing keeps the parser fast and correct.

---

## Regex Patterns

Patterns derived from real log analysis. Each was written and tested against live `journalctl` output before being added to the codebase.

```python
import re

# Session ID — correlation key
sshd_id = re.search(r"\[\d+\]", line)
clean_id = sshd_id.group().strip("[]")

# Hostname
hostname = re.search(r"[a-zA-Z0-9]+\.[a-zA-Z0-9]\S+", line)

# Timestamp
timestamp = re.search(r"[a-zA-Z]\w+\s[0-9]\w+\s\d+\d+\:\d+\d+\:\d+\d+", line)

# Username — capture group excludes UID suffix
username = re.search(r"\buser\s([a-zA-Z0-9]\S[^()]+)", line)
clean_username = username.group(1)

# UID
uid = re.search(r"\buid=(\d+)", line)
clean_uid = uid.group(1)

# Source IP
ip = re.search(r"\d+\.\d+\.\d+\.\d+", line)

# Outcome + Auth Method — two capture groups, one pattern
amo = re.search(r"\b(Accepted|Failed|Invalid)\s(\S+)", line)
outcome = amo.group(1)
auth_method = amo.group(2)
```

---

## SSH Log Anatomy

Understanding what the logs actually contain before writing a single line of code:

```
Apr 24 11:00:29 localhost.localdomain sshd-session[156384]: Accepted password for mudd-fedora from 100.93.55.19 port 34744 ssh2
Apr 24 11:00:29 localhost.localdomain sshd-session[156384]: pam_unix(sshd:session): session opened for user mudd-fedora(uid=1000) by mudd-fedora(uid=0)
Apr 24 11:00:43 localhost.localdomain sshd-session[156384]: pam_unix(sshd:session): session closed for user mudd-fedora
```

Every session follows an accept → open → close lifecycle. The session ID ties them together. ClearMudd uses this structure intentionally.

### What Anomalous Looks Like

```
Apr 24 11:00:27 localhost.localdomain sshd-session[156384]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=100.93.55.19 user=mudd-fedora
Apr 24 11:00:29 localhost.localdomain sshd-session[156384]: Failed password for mudd-fedora from 100.93.55.19 port 34744 ssh2
Apr 24 11:00:38 localhost.localdomain sshd-session[156384]: Failed password for mudd-fedora from 100.93.55.19 port 34744 ssh2
Apr 24 11:02:23 localhost.localdomain sshd-session[156474]: Invalid user mudd from 100.93.55.19 port 44006
Apr 24 11:02:31 localhost.localdomain sshd-session[156474]: Failed password for invalid user mudd from 100.93.55.19 port 44006 ssh2
Apr 24 11:02:38 localhost.localdomain sshd-session[156474]: Connection closed by invalid user mudd 100.93.55.19 port 44006 [preauth]
```

Key distinction: `Invalid user` means the account does not exist. This is a stronger indicator of probing than a failed password on a valid account. ClearMudd treats these differently.

---

## Infrastructure Context

ClearMudd runs on and monitors a five-device homelab:

| Device | OS | Role |
|--------|-----|------|
| ThinkPad T14 | Fedora 43 / Win11 | Primary dev machine |
| Dell Server | Ubuntu | Portainer, Netdata, n8n, Gitea |
| Raspberry Pi 4 | Raspberry Pi OS | Tailscale exit node, Netdata |
| Raspberry Pi Zero 2 W | Raspberry Pi OS | Netdata node |

Network is flat topology, Tailscale mesh, all services confined to `tailscale0`. No inbound exposure on physical interfaces. This means ClearMudd operates in a controlled threat environment — every source IP in the logs is a known mesh participant, making anomalies easier to identify.

---

## Roadmap

### v0 — Core Parser (current)
- [x] Identify target fields
- [x] Build and test regex patterns against real log output
- [ ] Line type routing logic
- [ ] For loop over journalctl stream
- [ ] Session data structure (dict keyed on session ID)
- [ ] Brute force detection logic
- [ ] Discord webhook notification

### v1 — Access Intelligence
- [ ] Historical baseline — what is normal for this network
- [ ] Anomaly scoring
- [ ] Report generation

### v2 — Multi-host
- [ ] Aggregate logs from multiple devices
- [ ] Cross-host correlation

---

## Author

Dillon — Mudd Labs  
*Rooted in craft. Reaching past the last mark.*
