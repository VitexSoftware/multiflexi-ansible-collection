# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is the `vitexus.multiflexi` Ansible Collection - an Ansible collection for managing MultiFlexi servers and their components. MultiFlexi is a business application platform that manages ERP/accounting systems, primarily targeting Czech/European markets.

## Architecture

The collection follows standard Ansible collection structure:

- **Roles**: `multiflexi_server` (installs MultiFlexi server), `run` (execution role)
- **Modules**: Custom Python modules in `plugins/modules/` that interact with `multiflexi-cli`
- **CLI Integration**: All modules use `multiflexi-cli` command-line tool rather than direct API calls
- **Database Support**: Supports SQLite, PostgreSQL, MySQL (MSSQL commented out)
- **Web Server**: Primarily Apache-based installation

### Key Modules
- `company.py` - Manage MultiFlexi companies (create/update/delete)
- `multiflexi_info.py` - Gather system facts via `multiflexi-cli appstatus`
- `user.py`, `application.py`, `job.py`, `topic.py` - Various entity management
- `credential.py`, `credential_type.py` - Authentication management

### Module Pattern
All modules follow this idempotent pattern:
1. Use `multiflexi-cli <entity> get` to check current state
2. Only create with `multiflexi-cli <entity> create` if resource doesn't exist
3. Use `multiflexi-cli <entity> update` if resource exists but differs
4. Report `changed: false` when no action needed

## Common Development Tasks

### Build and Install Collection
```bash
# Build the collection
ansible-galaxy collection build

# Install locally
ansible-galaxy collection install vitexus-multiflexi-*.tar.gz --force

# Install from requirements
ansible-galaxy collection install -r requirements.yml
```

### Testing
```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests  
python -m pytest tests/integration/

# Test specific module
python -m pytest tests/unit/plugins/modules/test_user.py

# Demo playbook execution
make demo
make debian13
```

### Linting and Quality
```bash
# Ansible lint (via GitHub Actions)
ansible-lint

# Collection sanity tests (via GitHub Actions)
ansible-test sanity
```

### CLI Documentation
```bash
# Update CLI documentation
make describecli
# This generates docs/multiflexi-cli.json with current CLI interface
```

### Development Environment
The collection uses:
- Python 3.9+ requirement
- `multiflexi-cli` as primary interface (not direct API)
- Development containers available in `.devcontainer/`
- MySQL connector Python dependency in `requirements.txt`

### Module Development Rules
1. **Idempotency**: All modules must check existing state before making changes
2. **CLI-first**: Use `multiflexi-cli` commands, not direct API calls
3. **Debug support**: Print CLI commands and output when `ansible-playbook -vv` used
4. **Error handling**: Use proper Ansible module patterns (fail_json, exit_json)
5. **JSON validation**: For any `*.app.json` files, validate against schema at https://raw.githubusercontent.com/VitexSoftware/php-vitexsoftware-multiflexi-core/refs/heads/main/multiflexi.app.schema.json

### Required External Dependencies
- `python3-mysql.connector` package must be installed on target MultiFlexi machines
- `multiflexi-cli` tool version 2.2.0 or newer must be available on managed systems

### CI/CD
- GitHub Actions run on all PRs
- Automated release to Ansible Galaxy on tagged releases
- Workflows include: changelog validation, ansible-lint, sanity tests, unit tests

### Collection Metadata
- Namespace: `vitexus`
- Name: `multiflexi` 
- Minimum Ansible: 2.15.0
- Supported platforms: Debian 10-12, Ubuntu 20.04-24.04
- License: MIT