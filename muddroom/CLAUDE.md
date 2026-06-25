# CLAUDE.md — Muddroom

Project-specific context for Claude. Paste alongside `mudd-labs/CLAUDE.md` at the start of every Muddroom session.

---

## What Muddroom Is

A Django-based homelab dashboard served over Tailscale. Named after a mudroom — the entry point where everything routes through. Displays live device reachability, service port health, and quick-launch links to homelab services.

**Repo:** `~/mudd-labs/muddroom/`
**Dev host:** ThinkPad (`tp-mudd`, `tag:t0`)
**Production target:** `dell-ubuntu` (`tag:t1`) — post-feature-complete
**Access:** `https://thinkpad.tail907d54.ts.net`

---

## Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0.6 |
| Language | Python 3.14.5 |
| Database | SQLite (dev) |
| Virtualenv | `myvenv/` — activate before any `manage.py` commands |
| Network | Tailscale Serve → `127.0.0.1:8000` |
| Automation | n8n (Docker, `dell-fedora`) |
| Alerting | Discord webhook |

---

## Models

### `Device`
```python
class Device(models.Model):
    name = models.CharField(max_length=200)
    tailscale_ip = models.GenericIPAddressField()
    is_reachable = models.BooleanField(default=True)
    last_checked = models.DateTimeField(null=True, blank=True)
```

### `Service`
```python
class Service(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)       # manual display control
    port_reachable = models.BooleanField(default=True)  # populated by webhook
    last_checked = models.DateTimeField(null=True, blank=True)
```

**Critical distinction:** `is_active` and `port_reachable` are intentionally separate fields. `is_active` is manual — an admin toggle for whether a service should appear on the hub at all. `port_reachable` is automated — set by the n8n port-check workflow. A service renders on the hub only if both are `True`.

---

## URLs

| Endpoint | View | Purpose |
|---|---|---|
| `/` | `hub` | Main dashboard — `@login_required` |
| `/webhooks/receive/` | `webhook_receiver` | Device health webhook (POST) |
| `/service-webhooks/receive/` | `service_webhook` | Service port health webhook (POST) |
| `/accounts/login/` | Django auth | Login page |
| `/admin/` | Django admin | Model management |

---

## Authentication

Hub view protected by `@login_required`. Unauthenticated requests redirect to `/accounts/login/`.

`LOGIN_URL` in `settings.py` must be uppercase — `lOGIN_URL` is silently ignored by Django (learned the hard way).

---

## n8n Workflows

**Host:** `dell-fedora`
**Schedule:** Every 15 minutes
**Script mount:** `/usr/local/bin/muddlabs/muddroom/` → `/scripts/muddroom/`

Workflow 1 (device ping) and Workflow 2 (port check) share a single Schedule Trigger, splitting into two parallel branches after the trigger node.

### Workflow 1 — Device Monitor

- Script: `device-ping.sh`
- Conf: `device.conf` — format: `<NAME> <TAILSCALE-IP>` (space-delimited)
- Webhook: `POST /webhooks/receive/`
- Payload key: `device` for name, `status` for CONFIRMED/UNCONFIRMED

### Workflow 2 — Port Check

- Script: `port-scan.sh`
- Conf: `port.conf` — format: `<NAME>,<IP>,<PORT>` (comma-delimited)
- Webhook: `POST /service-webhooks/receive/`
- Payload key: `name` for service name, `status` for CONFIRMED/UNCONFIRMED
- Uses `nc -z -w3 $ip $port` — checks transport layer only, not HTTP

**Note:** `nc` checks use Tailscale IPs and raw ports — not magic DNS hostnames. Tailscale Serve proxies HTTPS externally; `nc` operates at the transport layer and doesn't speak HTTP.

---

## Design System

| Token | Value |
|---|---|
| Eggshell | `#F7F5F0` |
| Forest green | `#1E3A2F` |
| Rose gold | `#C97B63` |
| Near black | `#1A1A1A` |
| Border | `#D4CFC6` |

**Fonts:** Space Grotesk (headings), DM Mono (labels/code), Inter (body)

---

## Known Issues / Deferred Work

| Item | Notes |
|---|---|
| Firewall rule (port 8000, tailscale zone) | Does not persist across reboots — re-add each session: `sudo firewall-cmd --zone=tailscale --add-port=8000/tcp` |
| Tailscale ACL | Temporary `tag:t1 → tag:t0 tcp:8000` grant — remove after migration to `dell-ubuntu` |
| `last_checked` UTC in Django admin | Cosmetic only — hub displays correct local time |
| Django dev server | Migrate to `dell-ubuntu` with Gunicorn + systemd for production |

---

## Immediate Next Steps

1. **Netdata API integration** — `pip install requests`, pull CPU/RAM/disk per device in `hub` view, render on device cards. Nodes: `dell-ubuntu` (19999), `muddpi` (19999), `pi-zero` (19999). Parent/child topology — verify via `netdata.conf` before assuming structure.
2. **Migrate Django to `dell-ubuntu`** — Gunicorn + systemd, update `ALLOWED_HOSTS`, configure Tailscale Serve on `dell-ubuntu`, remove temporary ACL rule and firewall exception.

---

## Notes for Claude

- I understand the architecture well enough to defend every decision in this file.
- Do not hand me working code without making sure I understand what it does first.
- When I propose an approach, push back if it's wrong — don't let it slide to keep momentum.
- Muddroom is an M3 portfolio piece. It needs to demonstrate systems thinking, not just working features.