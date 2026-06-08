# Demo Role

This role demonstrates the MultiFlexi Ansible Collection functionality by installing all available addon packages and creating sample data and configurations.

## Description

The demo role:
1. Verifies MultiFlexi is installed and running
2. Installs all available MultiFlexi addon packages from the apt repository (dynamically discovered, skiplist applied)
3. Creates a demo user with login credentials
4. Creates a demo company with basic information
5. Creates a sample application configuration
6. Creates a run template for automated execution
7. Schedules a job

The package installation step mirrors the logic from the `multiflexi-all` project: it runs `apt-cache search multiflexi` and excludes the following packages:

**Optional (infrastructure/database backends):** `multiflexi-all`, `multiflexi-mysql`, `multiflexi-pgsql`, `multiflexi-sqlite`, `multiflexi-podman`

**Blocked:** `multiflexi-pohoda-client-config`, `php-vitexsoftware-multiflexi-core`, `php-vitexsoftware-multiflexi-core-dev`, `php-vitexsoftware-multiflexi-server`, `php-vitexsoftware-multiflexi-server-dev`

**Regional bundles:** `multiflexi-eu`

**Conflicting or optional testing stacks:** `multiflexi-docker` (conflicts with `multiflexi-executor-docker`), `multiflexi-zabbix-selenium` (Selenium testing; not installed by default)

The skiplist is defined in `defaults/main.yml` as `demo_package_skiplist` and can be extended in your playbook. New packages published to the repository are picked up automatically without any changes to the role.

## Requirements

- MultiFlexi server must be installed and running
- `multiflexi-cli` must be available in PATH
- Appropriate permissions to create users, companies, and applications

## Role Variables

The role uses default values but can be customized:

- `demo_package_skiplist`: Package names excluded from bulk install (see `defaults/main.yml`)
- `demo_company_id`: Company identifier (default: "DEMO")
- `demo_app_id`: Application UUID (default: "78fa718c-7ca2-4a38-840e-8e5f0db06432")
- `scheduled`: Job scheduling (default: "now")
- `executor`: Execution engine (default: "native")

## Dependencies

- `multiflexi_server` APT tasks (`tasks/apt.yml`) are imported automatically before package installation to configure the VitexSoftware repository and upgrade `multiflexi-migrations`.

## Example Playbook

```yaml
- hosts: multiflexi_servers
  become: true
  roles:
    - vitexus.multiflexi.demo
```

## License

MIT

## Author Information

Created by Vítězslav Dvořák (vitex@vitexsoftware.com) for the MultiFlexi project.