# Claude Code project notes — ansible-role-netbox

This is an Ansible role that deploys NetBox as a Docker Compose stack
on Ubuntu hosts. It is location-agnostic and network-agnostic — all
site-specific values live in inventory, group_vars, and host_vars,
never in the role itself.

## Source of truth

**`DESIGN.md`** in this repo is the authoritative spec for the role.
Read it before making any non-trivial change. Variable names, schemas,
file layout, deployment model, upstream deviations, and all design
decisions live there.

If something in the code disagrees with `DESIGN.md`, `DESIGN.md` is
right unless explicitly told otherwise — flag the discrepancy and
ask before "fixing" the design to match the code.

## Conventions

* **Commits**: follow `AGENTS.md` exactly. Conventional Commits,
  imperative mood, bodies wrapped at 72, asterisk bullets.
* **Lint**: `.ansible-lint`, `.yamllint`, `.pre-commit-config.yaml`
  define the rules. Run `pre-commit run --all-files` before declaring
  work done.
* **Secrets**: never write a credential into a tracked file. Secrets
  are stored in Ansible Vault and templated into env files at deploy
  time. Use `no_log: true` on any task that touches them.
* **Modules**: prefer FQCNs (`community.docker.docker_compose_v2`,
  `ansible.builtin.template`, `ansible.builtin.copy`). The
  `.ansible-lint` rules require it.
* **Idempotency**: every task must be safe to re-run. The service task
  uses `wait: true` / `wait_timeout: 600` to survive the full NetBox
  migration window on fresh deployments.
* **Site-specific values**: hostnames, IP addresses, domain names, and
  region names must never appear in the role. They belong exclusively
  in `host_vars` or `group_vars`.

## Settled decisions — don't re-litigate

These are locked in `DESIGN.md`. Don't propose alternatives unless
the human raises them:

* Deployment model = rendered configuration (Option A). No git clone
  of netbox-docker on target hosts.
* `docker-compose.yml` is a static copy of upstream, maintained
  manually in `files/`. It is not templated.
* All env files are Jinja2 templates sourced from `defaults/main.yml`,
  `host_vars`, and Ansible Vault.
* `docker-compose.overlay.yml` (rendered from template) handles
  Traefik labels and `traefik_proxy` network membership. The
  deprecated `docker-compose.override.yml` pattern must not be used.
* `depends_on: condition: service_healthy` for postgres, redis, and
  redis-cache — prevents startup race on fresh deployments.
* `start_period: 300s` on the netbox healthcheck — gives migrations a
  safe runway on first deployment without affecting steady-state
  restarts.
* Each site has its own local Postgres and Valkey containers — no
  shared state between regions.
* All Docker image tags are pinned — no `latest` tags.

## Known upstream deviations

Both deviations are documented in `DESIGN.md` §"Known deviations from
upstream docker-compose.yml". When reviewing upstream diffs during
upgrades, preserve these changes:

* `depends_on` for netbox uses `condition: service_healthy` (upstream
  uses shorthand `condition: service_started`)
* `start_period` for netbox healthcheck is `300s` (upstream is `90s`)

## Testing locally

* `pre-commit run --all-files` — fast lint/format pass. Run before
  every commit.
* `molecule converge` then `molecule verify` — fast iteration during
  template / task work; skips the destroy/create cycle.
* `molecule test` — full role exercise per platform. Slow; run before
  declaring a change done.

## Working with the consumer side

This role is consumed from the user's playbooks repo (not in this
repo). Inventory layout, group_vars, and host_vars structure are
described in `DESIGN.md` §"Inventory structure" and §"Variable
hierarchy". When the human asks about consumer-side changes, ask
which inventory repo to operate on — it's not in this directory tree.

## When in doubt

Read `DESIGN.md`, then ask. The deployment model and design decisions
there came out of a multi-round design conversation; they're load-bearing.
