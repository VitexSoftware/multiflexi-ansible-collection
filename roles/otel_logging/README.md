OTEL Logging Engine Role
========================

Installs the logging engine that ingests and stores **OpenTelemetry logs/data**
for MultiFlexi and any OTEL-capable app, service or tool. The engine is Grafana
**Loki**, which natively ingests OTLP over HTTP (`POST /otlp/v1/logs`) and is
queryable from Grafana.

This role installs the *storage/query* engine only. Shipping logs into it
(per-host OpenTelemetry Collector agents, or apps exporting OTLP directly) is a
separate concern — point any OTLP client at `http://<host>:3100/otlp`.

Requirements
------------

- Debian/Ubuntu host with APT
- Internet access to fetch the Grafana APT key and the `loki` package

What This Role Does
-------------------

- Adds the Grafana APT repository (using `signed-by`, no `apt-key`)
- Installs the `loki` package (`.deb`)
- Deploys a single-binary Loki config with filesystem storage, TSDB schema
  (`v13`), native OTLP ingestion and compactor-based retention
- Enables and starts the `loki` systemd service

Role Variables
--------------

Defaults are in `defaults/main.yml`. Common knobs:

- `otel_logging_engine` (default `loki`) — logging engine to install. Only
  `loki` is implemented; the variable guards against future engine swaps.
- `otel_logging_http_listen_port` (default `3100`) — OTLP ingest + query API port.
- `otel_logging_data_dir` (default `/var/lib/loki`) — data/chunks/rules location.
- `otel_logging_config_file` (default `/etc/loki/config.yml`) — config path
  (matches the Grafana Debian package default).
- `otel_logging_retention_enabled` / `otel_logging_retention_period`
  (defaults `true` / `2160h` = 90 days) — audit retention via the compactor.
- `otel_logging_allow_structured_metadata` (default `true`) — required for OTLP.
- `otel_logging_auth_enabled` (default `false`) — single-tenant when `false`
  (no `X-Scope-OrgID` header required).
- `otel_logging_otlp_index_labels` — OTEL resource attributes promoted to Loki
  index labels (keep the set small; default `service.name`, `service.namespace`,
  `deployment.environment`). Everything else is stored as structured metadata.
- Repository: `otel_logging_repo_url`, `otel_logging_repo_component`,
  `otel_logging_repo_gpg_key`, `otel_logging_keyring_path`.

Example Playbook
----------------

```yaml
- name: Install the OTEL logging engine (Loki)
  hosts: grafana
  become: true
  roles:
    - role: vitexus.multiflexi.otel_logging
      vars:
        otel_logging_retention_period: "4320h"   # 180 days
```

Verify OTLP ingestion:

```bash
# Loki is ready to accept writes/queries
curl -s http://localhost:3100/ready

# After a collector/app sends OTLP logs, query them in Grafana Explore, e.g.:
#   {service_name="multiflexi-demo"}
```

License
-------

MIT

Author Information
------------------

VitexSoftware — https://vitexsoftware.com
