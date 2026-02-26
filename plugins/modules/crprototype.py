#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: crprototype
short_description: Manage credential prototypes in MultiFlexi

description:
    - This module allows you to manage credential prototypes (JSON-based credential type definitions) in MultiFlexi.
    - Supports list, get, create, update, delete, import-json, export-json, validate-json, and sync operations.

author:
    - Vitex (@Vitexus)

version_added: "2.4.0"

options:
    state:
        description:
            - The desired state or operation for the credential prototype.
        required: true
        type: str
        choices: ['present', 'absent', 'list', 'import', 'export', 'validate', 'sync']
    prototype_id:
        description:
            - The ID of the credential prototype.
        required: false
        type: int
    uuid:
        description:
            - The UUID of the credential prototype.
        required: false
        type: str
    code:
        description:
            - The code of the credential prototype.
        required: false
        type: str
    name:
        description:
            - Name of the credential prototype.
        required: false
        type: str
    description:
        description:
            - Description of the credential prototype.
        required: false
        type: str
    prototype_version:
        description:
            - Version of the credential prototype.
        required: false
        type: str
    logo:
        description:
            - Logo URL of the credential prototype.
        required: false
        type: str
    url:
        description:
            - Homepage URL of the credential prototype.
        required: false
        type: str
    file:
        description:
            - Path to JSON file for import/export/validate operations.
        required: false
        type: str
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: List all credential prototypes
  vitexus.multiflexi.crprototype:
    state: list

- name: Get a credential prototype by ID
  vitexus.multiflexi.crprototype:
    state: present
    prototype_id: 1

- name: Get a credential prototype by UUID
  vitexus.multiflexi.crprototype:
    state: present
    uuid: "d3d3ae58-d64a-4ab4-afb5-ba439ffc8587"

- name: Create a credential prototype
  vitexus.multiflexi.crprototype:
    state: present
    code: "my-cred"
    name: "My Credential"
    description: "A custom credential prototype"
    url: "https://example.com"

- name: Delete a credential prototype
  vitexus.multiflexi.crprototype:
    state: absent
    prototype_id: 1

- name: Import credential prototype from JSON
  vitexus.multiflexi.crprototype:
    state: import
    file: "/path/to/prototype.json"

- name: Export credential prototype to JSON
  vitexus.multiflexi.crprototype:
    state: export
    prototype_id: 1
    file: "/path/to/export.json"

- name: Validate credential prototype JSON file
  vitexus.multiflexi.crprototype:
    state: validate
    file: "/path/to/prototype.json"

- name: Sync credential prototypes
  vitexus.multiflexi.crprototype:
    state: sync
"""

RETURN = """
crprototype:
    description: The credential prototype object or list of prototypes.
    type: dict or list
    returned: always
msg:
    description: A message describing the action taken.
    type: str
    returned: always
"""


def run_cli_command(args, module=None):
    verbosity = 0
    if module and hasattr(module, '_verbosity'):
        try:
            verbosity = int(module._verbosity)
        except (TypeError, ValueError):
            verbosity = 0
    if verbosity >= 2 and module is not None:
        module.warn("[DEBUG] Running command: {}".format(' '.join(args)))
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        if verbosity >= 2 and module is not None:
            module.warn("[DEBUG] CLI output: {}".format(result.stdout.strip()))
        return result.stdout
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else ''
        stderr = e.stderr.strip() if e.stderr else ''
        if verbosity >= 2 and module is not None:
            module.warn("[DEBUG] CLI error: {}".format(stderr))
        try:
            if stdout:
                data = json.loads(stdout)
                if isinstance(data, dict) and data.get('status') == 'not found':
                    return stdout
        except Exception:
            pass
        raise Exception("multiflexi-cli error: {}".format(stderr or stdout or str(e)))


def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'absent', 'list', 'import', 'export', 'validate', 'sync']),
        prototype_id=dict(type='int', required=False),
        uuid=dict(type='str', required=False),
        code=dict(type='str', required=False),
        name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        prototype_version=dict(type='str', required=False),
        logo=dict(type='str', required=False),
        url=dict(type='str', required=False),
        file=dict(type='str', required=False),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        crprototype=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'crprototype']

    try:
        if state == 'list':
            args = cli_base + ['list', '--format', 'json']
            output = run_cli_command(args, module=module)
            result['crprototype'] = json.loads(output)
            result['msg'] = "Retrieved credential prototype list"

        elif state == 'present':
            # Check if prototype exists
            existing = None
            if module.params.get('prototype_id'):
                args = cli_base + ['get', '--id', str(module.params['prototype_id']), '--format', 'json']
                output = run_cli_command(args, module=module)
                data = json.loads(output)
                if isinstance(data, dict) and data.get('id') and data.get('status') != 'not found':
                    existing = data
            elif module.params.get('uuid'):
                args = cli_base + ['get', '--uuid', module.params['uuid'], '--format', 'json']
                output = run_cli_command(args, module=module)
                data = json.loads(output)
                if isinstance(data, dict) and data.get('id') and data.get('status') != 'not found':
                    existing = data
            elif module.params.get('code'):
                args = cli_base + ['get', '--code', module.params['code'], '--format', 'json']
                output = run_cli_command(args, module=module)
                data = json.loads(output)
                if isinstance(data, dict) and data.get('id') and data.get('status') != 'not found':
                    existing = data

            if existing:
                # Update
                update_args = cli_base + ['update', '--id', str(existing['id'])]
                changed = False
                for field, cli_opt in [('name', '--name'), ('description', '--description'),
                                       ('prototype_version', '--prototype-version'),
                                       ('logo', '--logo'), ('url', '--url'), ('code', '--code')]:
                    val = module.params.get(field)
                    if val is not None and str(val) != str(existing.get(field, '')):
                        update_args += [cli_opt, str(val)]
                        changed = True

                if not changed:
                    result['crprototype'] = existing
                    result['msg'] = "Credential prototype already up to date"
                    module.exit_json(**result)
                    return

                if module.check_mode:
                    result['changed'] = True
                    result['crprototype'] = existing
                    module.exit_json(**result)
                    return

                update_args += ['--format', 'json']
                output = run_cli_command(update_args, module=module)
                result['crprototype'] = json.loads(output)
                result['changed'] = True
                result['msg'] = "Updated credential prototype"
            else:
                # Create
                create_args = cli_base + ['create']
                for field, cli_opt in [('name', '--name'), ('description', '--description'),
                                       ('code', '--code'), ('prototype_version', '--prototype-version'),
                                       ('logo', '--logo'), ('url', '--url'), ('uuid', '--uuid')]:
                    val = module.params.get(field)
                    if val is not None:
                        create_args += [cli_opt, str(val)]

                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = "Would create credential prototype"
                    module.exit_json(**result)
                    return

                create_args += ['--format', 'json']
                output = run_cli_command(create_args, module=module)
                result['crprototype'] = json.loads(output)
                result['changed'] = True
                result['msg'] = "Created credential prototype"

        elif state == 'absent':
            if not module.params.get('prototype_id'):
                module.fail_json(msg="prototype_id is required for absent state")

            # Check if exists
            args = cli_base + ['get', '--id', str(module.params['prototype_id']), '--format', 'json']
            try:
                output = run_cli_command(args, module=module)
                data = json.loads(output)
                if isinstance(data, dict) and data.get('status') == 'not found':
                    result['msg'] = "Credential prototype not found"
                    module.exit_json(**result)
                    return
            except Exception:
                result['msg'] = "Credential prototype not found"
                module.exit_json(**result)
                return

            if module.check_mode:
                result['changed'] = True
                result['msg'] = "Would delete credential prototype"
                module.exit_json(**result)
                return

            args = cli_base + ['delete', '--id', str(module.params['prototype_id']), '--format', 'json']
            output = run_cli_command(args, module=module)
            result['changed'] = True
            result['msg'] = "Deleted credential prototype"

        elif state == 'import':
            if not module.params.get('file'):
                module.fail_json(msg="file parameter is required for import operation")

            if module.check_mode:
                result['changed'] = True
                result['msg'] = "Would import credential prototype from {}".format(module.params['file'])
                module.exit_json(**result)
                return

            args = cli_base + ['import-json', '--file', module.params['file'], '--format', 'json']
            output = run_cli_command(args, module=module)
            result['crprototype'] = json.loads(output)
            result['changed'] = True
            result['msg'] = "Imported credential prototype from {}".format(module.params['file'])

        elif state == 'export':
            if not module.params.get('file'):
                module.fail_json(msg="file parameter is required for export operation")
            if not (module.params.get('prototype_id') or module.params.get('uuid')):
                module.fail_json(msg="prototype_id or uuid is required for export operation")

            if module.check_mode:
                result['changed'] = True
                result['msg'] = "Would export credential prototype to {}".format(module.params['file'])
                module.exit_json(**result)
                return

            args = cli_base + ['export-json', '--file', module.params['file'], '--format', 'json']
            if module.params.get('prototype_id'):
                args.extend(['--id', str(module.params['prototype_id'])])
            elif module.params.get('uuid'):
                args.extend(['--uuid', module.params['uuid']])

            output = run_cli_command(args, module=module)
            result['crprototype'] = json.loads(output)
            result['changed'] = True
            result['msg'] = "Exported credential prototype to {}".format(module.params['file'])

        elif state == 'validate':
            if not module.params.get('file'):
                module.fail_json(msg="file parameter is required for validate operation")

            args = cli_base + ['validate-json', '--file', module.params['file'], '--format', 'json']
            output = run_cli_command(args, module=module)
            result['crprototype'] = json.loads(output)
            result['msg'] = "Validated credential prototype file {}".format(module.params['file'])

        elif state == 'sync':
            if module.check_mode:
                result['changed'] = True
                result['msg'] = "Would sync credential prototypes"
                module.exit_json(**result)
                return

            args = cli_base + ['sync', '--format', 'json']
            output = run_cli_command(args, module=module)
            result['crprototype'] = json.loads(output)
            result['changed'] = True
            result['msg'] = "Synced credential prototypes"

    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
