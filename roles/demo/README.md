# Demo Role

This role demonstrates the MultiFlexi Ansible Collection functionality by creating sample data and configurations.

## Description

The demo role creates:
- A demo user with login credentials
- A demo company with basic information
- A sample application configuration
- A run template for automated execution
- A scheduled job
- Credential types and topics for testing

## Requirements

- MultiFlexi server must be installed and running
- `multiflexi-cli` must be available in PATH
- Appropriate permissions to create users, companies, and applications

## Role Variables

The role uses default values but can be customized:

- `demo_company_id`: Company identifier (default: "DEMO")
- `demo_app_id`: Application UUID (default: "78fa718c-7ca2-4a38-840e-8e5f0db06432")
- `scheduled`: Job scheduling (default: "now")
- `executor`: Execution engine (default: "native")

## Dependencies

None

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