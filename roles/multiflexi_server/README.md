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

- `multiflexi_server_db_type` (string)
  - Default: `sqlite`
  - Primary variable controlling which DB-specific package set is installed.

- `multiflexi_server_database_type` (string | alias)
  - Default: `null`
  - Optional alias; if set, it takes precedence over `multiflexi_server_db_type` in this role.

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

Behavior Notes
--------------

- Database tasks include `mysql.yml` when the effective DB type equals `mysql`.
- Package tasks use the effective DB type to install `multiflexi-<db>` and related components.
- Effective DB type resolution:
  - `multiflexi_server_database_type | default(multiflexi_server_db_type)`

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
