# ansible-role-netbox

Deploys NetBox as a Docker Compose stack on Ubuntu/Debian hosts.
See [DESIGN.md](DESIGN.md) for architecture, variable hierarchy, upgrade process, and all design decisions.

## Requirements

- Ubuntu 24.04+ or Debian 12+
- Docker with the Compose plugin installed and running (soft dependency — role asserts this at runtime)
- The `traefik_proxy` external Docker network must exist on the target host before this role runs

## Quick start

```yaml
# playbooks/netbox.yml
- name: NetBox docker container
  hosts: netbox
  roles:
    - role: realtime.netbox
```

Minimum variables required per host (in `host_vars/<hostname>/vars.yml`):

```yaml
netbox_fqdn: netbox.example.com
netbox_email_from: netbox@example.com
netbox_csrf_trusted_origins: "https://netbox.example.com"
```

Secrets required in Ansible Vault (`host_vars/<hostname>/vault.yml`):

```yaml
netbox_db_password: "<generated>"
netbox_redis_password: "<generated>"
netbox_redis_cache_password: "<generated>"
netbox_secret_key: "<generated>"       # min 50 chars
netbox_api_token_pepper: "<generated>" # min 50 chars
```

Generate secrets with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

## First login

On a fresh deployment the netbox-docker entrypoint creates a superuser automatically:

- **Username:** `admin`
- **Password:** `admin`

> **⚠️ Change this password immediately after first login.** The default credentials are
> publicly known. Navigate to the top-right user menu → Profile → Change Password, or use
> the Django admin at `https://<netbox_fqdn>/admin/`.

## Operations

### Stop the NetBox stack

Run on the target host. Stops all NetBox containers but leaves volumes intact — data is preserved.

```bash
docker compose \
  -f /opt/netbox/docker-compose.yml \
  -f /opt/netbox/docker-compose.overlay.yml \
  --project-name netbox \
  down
```

### Remove and purge all NetBox data volumes

**Destructive — all NetBox data (database, media, reports, scripts, Redis) will be permanently deleted.**

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

After wiping volumes, the next Ansible run will reinitialize the NetBox database from scratch.
