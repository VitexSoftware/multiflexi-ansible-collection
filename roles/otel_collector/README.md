OTEL Collector Agent Role
=========================

Deploys the **OpenTelemetry Collector (contrib)** as a per-host agent that ships
the **systemd journal** — and OTLP from local apps/MCP servers — to the OTEL
logging engine (Loki). This is the universal auditability backbone: every
service under systemd is captured without per-application instrumentation.

Requirements
------------

- Debian/Ubuntu host with systemd and internet access to fetch the release `.deb`
- An OTEL logging engine / Loki OTLP endpoint reachable from the host
  (see the `otel_logging` role)

What This Role Does
-------------------

- Installs `otelcol-contrib` from the official OpenTelemetry release `.deb`
- Deploys `/etc/otelcol-contrib/config.yaml` with:
  - receivers: `journald` (systemd journal) and `otlp` (gRPC 4317 / HTTP 4318)
  - processors: `resourcedetection`, `resource` (stamps `service.namespace`,
    `deployment.environment`, `service.name`), `batch`
  - exporter: `otlphttp/loki` to the Loki OTLP endpoint (`/otlp` → `/v1/logs`)
- Installs a systemd drop-in so the agent runs as root (to read the full journal)
- Enables and (re)starts the `otelcol-contrib` service

Role Variables
--------------

Defaults are in `defaults/main.yml`. Common knobs:

- `otel_collector_version` (default `0.156.0`) — otelcol-contrib release to install.
- `otel_collector_logs_endpoint` (default `http://127.0.0.1:3100/otlp`) — Loki
  OTLP endpoint; the `otlphttp` exporter appends `/v1/logs`.
- `otel_collector_otlp_grpc_endpoint` / `otel_collector_otlp_http_endpoint`
  (defaults `0.0.0.0:4317` / `0.0.0.0:4318`) — OTLP receiver binds.
- `otel_collector_service_namespace` / `otel_collector_deployment_environment`
  (defaults `multiflexi` / `test`) — resource attributes → Loki index labels.
- `otel_collector_journald_enabled` (default `true`),
  `otel_collector_journald_start_at` (default `end`),
  `otel_collector_journald_units` (default `[]` = all units).
- `otel_collector_run_as_root` (default `true`) — run the agent as root so it can
  read the journal and log files.

Example Playbook
----------------

```yaml
- name: Deploy the OTEL Collector agent
  hosts: all
  become: true
  roles:
    - role: vitexus.multiflexi.otel_collector
      vars:
        otel_collector_logs_endpoint: "http://loki.internal:3100/otlp"
        otel_collector_deployment_environment: production
```

Verify:

```bash
otelcol-contrib validate --config=/etc/otelcol-contrib/config.yaml
logger -t probe "hello audit $(date +%s)"
# then query Loki: {service_namespace="multiflexi"} |= "hello audit"
```

License
-------

MIT

Author Information
------------------

VitexSoftware — https://vitexsoftware.com
