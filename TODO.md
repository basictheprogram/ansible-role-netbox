# TODO

Items flagged during the `ansible-sync-role` sync (2026-07-16) that were not
resolved in that session.

## 1. Apply by hand: `.pre-commit-config.yaml` ruff rev bump

Cowork's write/edit protection blocked this file (a known, reproducible
issue — see the skill's `references/known-issues.md`). You agreed to bump
the pinned `ruff-pre-commit` rev to match `_template/.pre-commit-config.yaml`;
apply this one-line change by hand:

```diff
--- a/.pre-commit-config.yaml
+++ b/.pre-commit-config.yaml
@@ -29,7 +29,7 @@
       - id: gitleaks

   - repo: https://github.com/astral-sh/ruff-pre-commit
-    rev: v0.15.14
+    rev: v0.15.16
     hooks:
       - id: ruff
         name: Ruff check
```

## 2. Rename in progress: role/repo identity is now `netbox_docker`

Per your later instruction (2026-07-16, same day), the role was renamed
in-place to `realtime.netbox_docker` (`meta/main.yml` `role_name`,
`README.md`, `DESIGN.md`, `CLAUDE.md`, template header comments,
`molecule/default/converge.yml`, testinfra docstrings). By design, this
session only touched file contents inside the role directory — you said
you'd handle the rest outside Cowork:

* The physical directory (`roles/git_repository/ansible-role-netbox`) and
  the `roles/realtime.netbox` symlink in the `ansible-playbooks` repo are
  still named with the old `netbox` (no `_docker`) — rename both to
  `ansible-role-netbox_docker` / `realtime.netbox_docker` to match.
* `git remote -v` still shows origin as
  `git@github.com:basictheprogram/ansible-role-netbox-docker.git`
  (hyphenated `-docker`) — this doesn't match the new in-role naming
  convention (underscored `_docker`, required since Galaxy role names
  can't contain hyphens). Rename the actual GitHub repo and/or update the
  remote URL to `ansible-role-netbox_docker` once decided.
* You said you'd decide whether to leave a backward-compat
  `roles/realtime.netbox` symlink for existing consumer playbooks, or
  make this a clean break — neither was done from this session.

## 3. Debian 12 (bookworm) full security support ends next month

Per `scripts/platform-data.json`, Debian 12's full security-team support
ends 2026-08 (this role's molecule matrix and meta description were
generated in 2026-07). LTS coverage continues to 2028-06, so bookworm
was kept in the supported-platform list — but it's worth revisiting
before full-support EOL if LTS-only support becomes unacceptable for
this role's deployment targets.

## 4. New testinfra suite doesn't cover container/service health

The `molecule/default/tests/` suite added this session (`test_directories.py`,
`test_config.py`, `test_env.py`, `test_compose.py`) covers deploy directory
layout, static config files, rendered env file existence/permissions/content,
and compose file presence. It does **not** verify that the Docker Compose
stack actually comes up healthy (NetBox web response, `docker compose ps`
state) — the target isn't network-reachable from the testinfra `host`
fixture in the way this role's tests are structured, and container health
depends on a long (`600s`) `start_period`. If deeper service-level coverage
is wanted later, consider a `host.run()`-based check against
`docker compose ps --format json` inside `test_compose.py`.

## 5. No `meta/argument_specs.yml`

Optional per this skill's Step 4 (only required to fix if one already
exists with placeholder content). None exists for this role. Not created
this session — low priority, but would give role-variable validation and
better `ansible-doc` output if added later.
