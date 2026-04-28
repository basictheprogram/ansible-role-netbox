# Ansible Role: netbox

[![CI](https://github.com/basictheprogram/ansible-role-netbox/actions/workflows/ci.yml/badge.svg)](https://github.com/basictheprogram/ansible-role-netbox/actions/workflows/ci.yml)
[![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-netbox-blue.svg?style=popout-square)](https://galaxy.ansible.com/realtime/netbox)
[![Ansible Role](https://img.shields.io/ansible/role/d/realtime/netbox.svg?style=popout-square)](https://galaxy.ansible.com/realtime/netbox)

An Ansible-managed implementation of the [netbox-docker](https://github.com/netbox-community/netbox-docker)
project. Rather than cloning netbox-docker on each host and tweaking files by hand,
this role renders all configuration from templates and variables at deploy time —
Ansible owns the full lifecycle. Each site is fully isolated with its own Postgres
and Valkey instances.

> For full architecture, variable hierarchy, upgrade process, and all design decisions see [DESIGN.md](DESIGN.md).

## Requirements

- Ubuntu 24.04 or Ubuntu 26.04
- Docker Engine with the Compose plugin installed and running
  (soft dependency — role asserts this at runtime)
- `community.docker` collection >= 3.0
- The `traefik_proxy` external Docker network must exist on the target host
  before this role runs (created by `ansible-role-traefik`)

## Installation

```bash
ansible-galaxy install realtime.netbox
```

Or pin to this repository in `requirements.yml`:

```yaml
roles:
  - name: realtime.netbox
    src: https://github.com/basictheprogram/ansible-role-netbox
    version: main
```

## Role Variables

All variables with their defaults live in `defaults/main.yml`. Variables are
split across three layers — the role itself never contains site-specific values.

| Layer | Location | Contains |
| :--- | :--- | :--- |
| Role defaults | `defaults/main.yml` | Safe defaults: versions, deploy dir, feature flags |
| Role constants | `vars/main.yml` | Internal paths derived from `netbox_deploy_dir` |
| Group config | `group_vars/netbox.yml` | Shared non-secret config across all NetBox hosts |
| Host identity | `host_vars/<hostname>/vars.yml` | Per-site values: FQDN, email relay, region |
| Secrets | Ansible Vault (host) | Passwords, keys, tokens |

### Image versions

All tags are pinned — bump deliberately via controlled rollout. Upstream releases
are tracked at <https://github.com/netbox-community/netbox-docker/releases>.

```yaml
netbox_version: "v4.5-4.0.2"        # tracks upstream netbox-docker releases
netbox_postgres_version: "18-alpine"
netbox_valkey_version: "9.0-alpine"
```

### Deploy directory

```yaml
netbox_deploy_dir: /opt/netbox
netbox_compose_project_name: netbox
```

### Database

```yaml
netbox_db_host: postgres
netbox_db_name: netbox
netbox_db_user: netbox
```

### Redis / Valkey

Two Valkey instances run per site: one for general use, one for caching.
No shared Redis between sites.

```yaml
netbox_redis_host: redis
netbox_redis_database: 0
netbox_redis_ssl: false

netbox_redis_cache_host: redis-cache
netbox_redis_cache_database: 1
netbox_redis_cache_ssl: false
```

### NetBox application settings

```yaml
netbox_cors_origin_allow_all: true
netbox_graphql_enabled: true
netbox_metrics_enabled: false
netbox_webhooks_enabled: true
netbox_skip_superuser: false

# Required when NetBox is behind a reverse proxy (e.g. Traefik).
# Set to the full https:// URL matching netbox_fqdn.
netbox_csrf_trusted_origins: ""
```

### Per-host variables

The following must be defined in `host_vars/<hostname>/vars.yml` — they have
no safe default and the role will fail preflight without them:

| Variable | Description |
| :--- | :--- |
| `netbox_fqdn` | Fully-qualified domain name for the NetBox instance |
| `netbox_email_from` | From address for outgoing email |
| `netbox_email_server` | SMTP relay hostname |
| `netbox_csrf_trusted_origins` | Full `https://` URL matching `netbox_fqdn` |

### Secrets (Ansible Vault)

Store in `host_vars/<hostname>/vault.yml`. Preflight assertions will fail fast
if any secret is missing or too short, before any containers are touched.

| Variable | Description |
| :--- | :--- |
| `netbox_db_password` | Postgres password |
| `netbox_redis_password` | Valkey (Redis) password |
| `netbox_redis_cache_password` | Valkey cache password |
| `netbox_secret_key` | Django `SECRET_KEY` — min 50 chars |
| `netbox_api_token_pepper` | NetBox `API_TOKEN_PEPPER` — min 50 chars |

Generate secrets with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Compose stack state

```yaml
netbox_compose_state: present   # set to 'absent' to tear down (data volumes preserved)
```

## Quick start

```yaml
# playbooks/netbox.yml
- name: Deploy NetBox
  hosts: netbox
  roles:
    - role: realtime.netbox
```

Minimum `host_vars/<hostname>/vars.yml`:

```yaml
netbox_fqdn: netbox.example.com
netbox_email_from: netbox@example.com
netbox_email_server: relay.example.com
netbox_csrf_trusted_origins: "https://netbox.example.com"
```

Minimum `host_vars/<hostname>/vault.yml`:

```yaml
netbox_db_password: "<generated>"
netbox_redis_password: "<generated>"
netbox_redis_cache_password: "<generated>"
netbox_secret_key: "<generated>"         # min 50 chars
netbox_api_token_pepper: "<generated>"   # min 50 chars
```

## First login

On a fresh deployment the netbox-docker entrypoint creates a superuser
automatically:

- **Username:** `admin`
- **Password:** `admin`

> **⚠️ Change this password immediately after first login.** The default credentials
> are publicly known. Navigate to the top-right user menu → Profile → Change Password,
> or use the Django admin at `https://<netbox_fqdn>/admin/`.

## Operations

### Stop the NetBox stack

Run on the target host. Stops all NetBox containers but leaves volumes intact —
data is preserved.

```bash
docker compose \
  -f /opt/netbox/docker-compose.yml \
  -f /opt/netbox/docker-compose.overlay.yml \
  --project-name netbox \
  down
```

### Remove and purge all NetBox data volumes

**Destructive — all NetBox data (database, media, reports, scripts, Redis) will
be permanently deleted.**

Stop the stack first (see above), then:

```bash
docker volume rm \
  netbox_netbox-postgres \
  netbox_netbox-redis-data \
  netbox_netbox-redis-cache-data \
  netbox_netbox-media-files \
  netbox_netbox-reports-files \
  netbox_netbox-scripts-files
```

Alternatively, stop and remove volumes in a single command:

```bash
docker compose \
  -f /opt/netbox/docker-compose.yml \
  -f /opt/netbox/docker-compose.overlay.yml \
  --project-name netbox \
  down --volumes
```

After wiping volumes, the next Ansible run will reinitialize the NetBox database
from scratch.
