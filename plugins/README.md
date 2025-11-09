# Collections Plugins Directory

This directory contains various plugins for the MultiFlexi Ansible collection. Each plugin is placed in a folder that
is named after the type of plugin it is in.

## MultiFlexi Modules

The `modules` directory contains comprehensive modules for managing MultiFlexi instances:

### Core Entity Management

- **application**: Manage applications (create, update, delete, import/export JSON, validate)
- **company**: Manage companies and their settings
- **user**: Manage users and their accounts
- **job**: Manage job execution and scheduling
- **runtemplate**: Manage run templates for automated execution

### Credential and Security Management

- **credential**: Manage credential instances
- **credential_type**: Manage credential types (with JSON import/export/validation)
- **token**: Manage authentication tokens (create, generate, update)
- **encryption**: Manage encryption keys and status
- **user_data_erasure**: Handle GDPR user data erasure requests

### System Operations

- **multiflexi_status**: Get comprehensive system status
- **queue**: Manage job queues (list, truncate)
- **prune**: Prune logs and jobs to maintain performance
- **artifact**: Manage job artifacts and outputs
- **companyapp**: Manage company-application relationships

### Key Features

- **JSON Operations**: Many modules support JSON import/export for bulk operations
- **Schema Validation**: Automatic validation against MultiFlexi schemas
- **CLI Integration**: All modules use the `multiflexi-cli` command-line tool
- **Check Mode Support**: Dry-run support for safe operations
- **Comprehensive Error Handling**: Detailed error reporting and validation

All modules follow Ansible best practices and provide consistent interfaces for managing MultiFlexi infrastructure.

## Plugin Directory Structure

Here is the directory structure for the plugins:

```text
└── plugins
    ├── action
    ├── become
    ├── cache
    ├── callback
    ├── cliconf
    ├── connection
    ├── filter
    ├── httpapi
    ├── inventory
    ├── lookup
    ├── module_utils
    ├── modules           # MultiFlexi management modules
    ├── netconf
    ├── shell
    ├── strategy
    ├── terminal
    ├── test
    └── vars
```

A full list of plugin types can be found at [Working With Plugins](https://docs.ansible.com/ansible-core/2.14/plugins/plugins.html).
