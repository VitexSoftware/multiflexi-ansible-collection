# Demo Proxy Role

Configures the Apache reverse proxy vhost that fronts a MultiFlexi backend
server behind a public domain, terminating TLS and forwarding to the
backend over plain HTTP.

## Description

The demo instance at demo.multiflexi.eu is split across two hosts: a public
edge server that terminates TLS and proxies to an internal backend server
running `multiflexi_server` + `demo`. This role manages the edge server's
vhost and must be applied to the edge host, not the backend.

It sets:

- `ProxyPreserveHost On` so the backend sees the real client-facing
  hostname and issues its session cookie for that domain rather than the
  backend's own address (browsers silently reject a cookie whose domain
  doesn't match the site they're on).
- `X-Forwarded-Proto: https` / `X-Forwarded-Host` on the proxied request,
  since the edge-to-backend hop is plain HTTP. Without this, a backend
  rule that redirects non-HTTPS requests fires on every proxied request
  and loops against the proxy's path prefix.

## Requirements

- A Let's Encrypt certificate must already exist for `demo_proxy_domain`
  (e.g. via `certbot --apache -d demo.multiflexi.eu`). This role does not
  issue certificates.

## Role Variables

- `demo_proxy_domain`: Public hostname of the vhost (default: `example.com` - override per deployment)
- `demo_proxy_backend_scheme`: Scheme used to reach the backend (default: `http`)
- `demo_proxy_backend_host`: Backend server address (default: `127.0.0.1` - override per deployment)
- `demo_proxy_backend_path`: Path prefix on the backend to proxy to (default: `/multiflexi/`)
- `demo_proxy_letsencrypt_live_dir`: Certificate directory (default: `/etc/letsencrypt/live/{{ demo_proxy_domain }}`)

## Example Playbook

```yaml
- hosts: multiflexi_demo_proxy
  roles:
    - vitexus.multiflexi.demo_proxy
```

## License

MIT

## Author Information

Created by Vítězslav Dvořák (vitex@vitexsoftware.com) for the MultiFlexi project.
