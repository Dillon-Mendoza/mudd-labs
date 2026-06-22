# Muddroom

A custom homelab dashboard built on Django, served over Tailscale. Named after a mudroom — the entry point where everything routes through. Displays live device reachability and quick-launch links to homelab services.

**Status:** Active development on ThinkPad (`tp-mudd`). Production migration to `dell-ubuntu` planned post-feature-complete.

---

## Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0.6 |
| Language | Python 3.14.5 |
| Database | SQLite (dev) |
| Network | Tailscale Serve |
| Automation | n8n (Docker, `dell-fedora`) |
| Alerting | Discord webhook |

---

## Infrastructure

| Device | Tag | Role |
|---|---|---|
| ThinkPad (`tp-mudd`) | `tag:t0` | Dev machine, Muddroom host |
| Dell Server — Ubuntu (`dell-ubuntu`) | `tag:t1` | Production migration target |
| Dell Server — Fedora VM (`dell-fedora`) | `tag:t1` | n8n Docker host |
| Pi 4 | `tag:t2` | Backup exit node, Netdata |
| Pi Zero 2W | `tag:t3` | Netdata only |
| Oracle Cloud (`mudd-cloud`) | `tag:cloud` | Primary exit node |

Muddroom is served via `tailscale serve` → `127.0.0.1:8000`, accessible at `https://thinkpad.tail907d54.ts.net`.

---

## Project Structure

```
muddroom/
├── manage.py
├── .env                          # secrets — never commit
├── .env.example                  # safe to commit
├── requirements.txt
├── myvenv/                       # activate before any manage.py commands
├── mysite/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── muddroom/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── apps.py
    ├── static/
    │   ├── css/
    │   │   └── muddroom.css
    │   └── img/
    │       └── muddlabs-logo.svg
    └── templates/
        ├── muddroom/
        │   ├── base.html
        │   └── hub.html
        └── registration/
            └── login.html
```

---

## Setup From Scratch

### 1. Clone and create environment

```bash
git clone <repo-url> ~/mudd-labs/muddroom
cd ~/mudd-labs/muddroom
python3 -m venv myvenv
source myvenv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your values
```

Required `.env` variables:

```
SECRET_KEY=<generate-with-python-secrets>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,<TAILSCALE-IP-T0>,<TAILSCALE-HOSTNAME-T0>
CSRF_TRUSTED_ORIGINS=https://<TAILSCALE-HOSTNAME-T0>
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create superuser

```bash
python manage.py createsuperuser
# Username: <admin-username>
```

### 5. Collect static files

```bash
python manage.py collectstatic
```

### 6. Start dev server

```bash
python manage.py runserver 0.0.0.0:8000
```

### 7. Configure Tailscale Serve

```bash
tailscale serve --bg http://127.0.0.1:8000
```

### 8. Open firewall for Tailscale interface (temporary — dev only)

```bash
sudo firewall-cmd --zone=tailscale --add-port=8000/tcp
```

Note: This rule does not persist across reboots. Re-add each session until Django is migrated to `dell-ubuntu`.

---

## Django Admin Setup

After setup, log into `/admin` and add:

### Devices

Add one `Device` record per Tailscale mesh device:

| Field | Value |
|---|---|
| name | Must match `device.conf` exactly — case sensitive |
| tailscale_ip | Device's Tailscale IP |
| is_reachable | Default `True` |
| last_checked | Leave blank — populated by webhook |

### Services

Add one `Service` record per homelab service:

| Field | Value |
|---|---|
| name | Display name |
| url | Full URL including port |
| description | Short description |
| icon | Emoji |
| is_active | `True` to display on hub |

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
    is_active = models.BooleanField(default=True)
```

---

## Webhook Receiver

**Endpoint:** `POST /webhooks/receive/`

**Authentication:** None (CSRF exempt — internal Tailscale network only)

**Expected payload:**

```json
[
  {"status": "CONFIRMED", "device": "mudd-cloud", "ip": "<TAILSCALE-IP>"},
  {"status": "UNCONFIRMED", "device": "muddpi", "ip": "<TAILSCALE-IP>"}
]
```

**Behavior:**
- `CONFIRMED` → sets `is_reachable = True`
- Any other status → sets `is_reachable = False`
- Device name not found in database → skips that device, continues processing remaining devices
- Updates `last_checked` timestamp on every processed device

---

## n8n Workflow — Muddroom Device Monitor

**Host:** `dell-fedora` (Docker)  
**Schedule:** Every 15 minutes  
**Script mount:** `/usr/local/bin/muddlabs/muddroom/` → `/scripts/muddroom/`

### Workflow nodes

```
Schedule Trigger
  → Execute Command (sh /scripts/muddroom/device-ping.sh)
  → Code in JavaScript (parse stdout into JSON array)
  → HTTP Request (POST to Django webhook)
  → If ($json.status == "ok")
      True branch: end (no action)
      False branch: Aggregate → HTTP Request (Discord alert)
```

### Code node

```javascript
let text = $input.first().json.stdout;
let split = text.split('\n');
let result = split.filter(line => line.trim());

return result.map(line => {
  const parts = line.split(' | ');
  return { json: { status: parts[0], device: parts[1], ip: parts[2] } };
});
```

### HTTP Request node (Django)

```
Method: POST
URL: https://<TAILSCALE-HOSTNAME-T0>/webhooks/receive/
Body Content Type: JSON
Body: {{ $input.all().map(item => item.json) }}
```

### Discord alert body

```json
{ "content": "Muddroom webhook failed — Django unreachable" }
```

---

## Script Files (`dell-fedora`)

### Directory structure

```
/usr/local/bin/muddlabs/
└── muddroom/
    ├── device-ping.sh
    └── device.conf
```

### Permissions

```bash
chmod +x /usr/local/bin/muddlabs/muddroom/device-ping.sh
chmod 644 /usr/local/bin/muddlabs/muddroom/device.conf
```

Note: `device.conf` is 644 (not 600) — n8n container runs as non-root and requires read access.

### `device.conf` format

```
<DEVICE-NAME-1> <TAILSCALE-IP-1>
<DEVICE-NAME-2> <TAILSCALE-IP-2>
```

Device names must exactly match Django admin `Device.name` — case sensitive.

---

## Design System

Pulled directly from the Mudd Labs logo palette.

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
| Firewall rule (port 8000, tailscale zone) | Does not persist across reboots — re-add manually each session |
| Tailscale ACL | Temporary `tag:t1 → tag:t0 tcp:8000` grant added for dev — remove after Django migrated to `dell-ubuntu` |
| `last_checked` displays UTC in Django admin | Cosmetic only — hub displays correct local time |
| Django running as dev server | Must migrate to `dell-ubuntu` with Gunicorn + systemd for production |
| Login gate | Auth exists but hub is currently accessible without login — `@login_required` decorator needed on `hub` view |

---

## Milestone Context

| Milestone | Status |
|---|---|
| M1 — Linux+, Python fundamentals, homelab documented | In progress |
| M2 — ClearMudd v0 live | Pending |
| M3 — Three deep portfolio projects (Muddroom counts as one) | In progress |
| M4 — First outside audience | Pending |
| M5 — First professional role | Pending |

---

## Immediate Next Steps

1. **Add `@login_required` to `hub` view** — enforce authentication, redirect to `/accounts/login/`
2. **Build Workflow 3 (port-check)** — service health via `nc -z -w3 $ip $port`, POST to separate endpoint or extend webhook receiver
3. **Add `requests` library** — build Netdata API calls in `hub` view, pull CPU/RAM/disk per device
4. **Render live Netdata metrics** on device cards
5. **Migrate Django to `dell-ubuntu`** — Gunicorn + systemd, update `ALLOWED_HOSTS`, configure Tailscale Serve on `dell-ubuntu`, remove temporary ACL rule and firewall exception