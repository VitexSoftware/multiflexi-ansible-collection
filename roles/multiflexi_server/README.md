MultiFlexi Server Role
======================

Installs and configures MultiFlexi server on Debian/Ubuntu systems using the official VitexSoftware repositories. The role is idempotent and configurable via variables.

Requirements
------------

- Debian/Ubuntu host with APT
- Python, Ansible
- Internet access to fetch repository GPG key and packages

What This Role Does
-------------------

- Adds the VitexSoftware APT repository (using signed-by; no apt-key)
- Installs and configures the selected database engine prerequisites (currently MySQL/MariaDB)
- Installs MultiFlexi components:
  - `multiflexi-<db>` meta package (e.g., `multiflexi-sqlite`, `multiflexi-mysql`)
  - `multiflexi-cli` (command line interface)
  - `multiflexi-api` (API service)
- Installs and enables Apache where applicable

Role Variables
--------------

Defaults are defined in `defaults/main.yml`.

- `multiflexi_server_database_engines` (list)
  - Default: `[sqlite, pgsql, mysql]`
  - Supported database backends; used for validation/conditions.

- `multiflexi_server_database_type` (string)
  - Default: `sqlite`
  - Canonical variable controlling which DB-specific package set is installed.

- `multiflexi_server_webserver_type` (string)
  - Default: `apache`
  - Web server to configure. Currently Apache is supported by the role tasks.

- `multiflexi_repository_channel` (string)
  - Default: `testing`
  - Choose repository channel: `testing` or `stable`.

- `multiflexi_repositories` (mapping)
  - Structure with `repo_url` and `gpg_key` for each channel. Defaults:
    - `testing.repo_url: http://repo.vitexsoftware.com`
    - `testing.gpg_key: http://repo.vitexsoftware.com/KEY.gpg`
    - `stable.repo_url: https://repo.multiflexi.eu`
    - `stable.gpg_key: https://repo.multiflexi.eu/KEY.gpg`

- `multiflexi_server_zabbix_host` (string | optional)
  - Default: `null`
  - Zabbix host used for monitoring integrations (reserved for future tasks/integration points).

- `multiflexi_server_zabbix_server` (string | optional)
  - Default: `null`
  - Zabbix server address (reserved for future tasks/integration points).

- `multiflexi_server_nodered_enabled` (bool | optional)
  - Default: `false`
  - When `true`, installs Node-RED + `node-red-contrib-multiflexi` + `multiflexi-eventor`,
    seeds a flow with a `multiflexi-catalog` node, wires the catalog feed and shows Node-RED
    in the MultiFlexi web Integrations menu.

- `multiflexi_server_nodered_http_root` (string | optional)
  - Default: `/node-red`
  - Reverse-proxy the Node-RED editor under this path on the existing (HTTPS) Apache
    vhost, served over TLS instead of the unencrypted `:1880` port. The role enables
    the `proxy`, `proxy_http`, `proxy_wstunnel` and `rewrite` Apache modules, drops
    `multiflexi-nodered.conf` and sets `httpAdminRoot` in Node-RED's `settings.js`.
    Set to `""` to disable the proxy and use direct `:1880` access.

- `multiflexi_server_nodered_url` (string | optional)
  - Default: `https://{{ ansible_fqdn }}{{ multiflexi_server_nodered_http_root }}/`
    (falls back to `http://{{ ansible_fqdn }}:1880/` when the proxy root is empty).
  - Node-RED editor URL linked from the Integrations menu.

- `multiflexi_server_nodered_app_url` (string | optional)
  - Default: `/multiflexi/`
  - Base URL of the MultiFlexi web image endpoints the catalog node fetches icons from.

- `multiflexi_server_nodered_admin_user` (string | optional)
  - Default: `demo`
  - Creates a Node-RED editor login (`adminAuth`) so the editor is not left open.
    Set to `""` to leave Node-RED's own `adminAuth` untouched.

- `multiflexi_server_nodered_admin_password_hash` (string | optional)
  - Default: bcrypt hash of `demo`.
  - The demo user's password as a Node-RED-format bcrypt hash (no `passlib`
    needed on the control node). Generate one with `node-red-admin hash-pw`.

- `multiflexi_server_nodered_admin_permissions` (string | optional)
  - Default: `*` (full access). Use `read` for a read-only demo.

- Other Node-RED knobs: `multiflexi_server_nodered_catalog_url`,
  `multiflexi_server_nodered_catalog_path`, `multiflexi_server_nodered_user`,
  `multiflexi_server_nodered_userdir`, `multiflexi_server_nodered_seed_flow`.

Behavior Notes
--------------

- Database tasks include `mysql.yml` when the effective DB type equals `mysql`.
- Package tasks use the effective DB type to install `multiflexi-<db>` and related components.
- Effective DB type is simply `multiflexi_server_database_type`.
- The Node-RED Integrations menu entry also needs a `multiflexi-web` build that includes the
  feature (it renders `NODERED_ENABLED`/`NODERED_URL`); reaching demo via `apt`.

Example Playbook
----------------

```yaml
- name: Install MultiFlexi server
  hosts: multiflexi_hosts
  become: true
  vars:
    multiflexi_server_database_type: mysql
    multiflexi_server_zabbix_host: magnymph.vitexsoftware.com
    multiflexi_server_zabbix_server: zabbix.spojenet.cz
    multiflexi_repository_channel: stable   # or 'testing'
  roles:
    - role: multiflexi_server
```

License
-------

MIT

Author Information
------------------

VitexSoftware — https://vitexsoftware.com
