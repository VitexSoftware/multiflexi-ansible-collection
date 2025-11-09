#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: credential_type
short_description: Manage credential types in Multiflexi

description:
    - This module allows you to get, update, and list credential types in Multiflexi via REST API.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the credential type.
        required: true
        type: str
        choices: ['present', 'absent', 'list', 'import', 'export', 'validate', 'remove-json']
    credential_type_id:
        description:
            - The ID of the credential type.
        required: false
        type: int
    uuid:
        description:
            - The UUID of the credential type.
        required: false
        type: str
    name:
        description:
            - Name of the credential type.
        required: false
        type: str
    file:
        description:
            - Path to JSON file for import/export/validate/remove-json operations.
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
- name: List all credential types
  credential_type:
    state: list

- name: Get a credential type by ID
  credential_type:
    state: present
    credential_type_id: 1

- name: Get a credential type by UUID
  credential_type:
    state: present
    uuid: "d3d3ae58-d64a-4ab4-afb5-ba439ffc8587"

- name: Update a credential type
  credential_type:
    state: present
    credential_type_id: 1
    name: "Updated API Key"

- name: Validate credential type JSON file
  credential_type:
    state: validate
    file: "/path/to/credtype.json"

- name: Import credential type from JSON
  credential_type:
    state: import
    file: "/path/to/credtype.json"

- name: Export credential type to JSON
  credential_type:
    state: export
    credential_type_id: 1
    file: "/path/to/export.json"

- name: Remove credential type based on JSON file
  credential_type:
    state: remove-json
    file: "/path/to/credtype.json"
"""

RETURN = """
credential_type:
    description: The credential type object or list of credential types.
    type: dict or list
    returned: always
"""

def run_cli_command(args):
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"multiflexi-cli error: {e.stderr.strip()}")

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'absent', 'list', 'import', 'export', 'validate', 'remove-json']),
        credential_type_id=dict(type='int', required=False),
        uuid=dict(type='str', required=False),
        name=dict(type='str', required=False),
        file=dict(type='str', required=False),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        credential_type=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'credtype']

    try:
        if state == 'list':
            args = cli_base + ['list', '--format', 'json']
            output = run_cli_command(args)
            result['credential_type'] = json.loads(output)
            result['msg'] = "Retrieved credential type list"
            
        elif state == 'present':
            # Get credential type by ID, UUID, or name
            if module.params.get('credential_type_id'):
                args = cli_base + ['get', '--id', str(module.params['credential_type_id']), '--format', 'json']
                output = run_cli_command(args)
                result['credential_type'] = json.loads(output)
                result['msg'] = f"Retrieved credential type {module.params['credential_type_id']}"
                
                # Update if name is provided
                if module.params.get('name'):
                    args = cli_base + ['update', '--id', str(module.params['credential_type_id']), 
                                     '--name', module.params['name'], '--format', 'json']
                    output = run_cli_command(args)
                    result['changed'] = True
                    result['msg'] = f"Updated credential type {module.params['credential_type_id']}"
                    
                    # Get updated credential type
                    args = cli_base + ['get', '--id', str(module.params['credential_type_id']), '--format', 'json']
                    output = run_cli_command(args)
                    result['credential_type'] = json.loads(output)
                    
            elif module.params.get('uuid'):
                args = cli_base + ['get', '--uuid', module.params['uuid'], '--format', 'json']
                output = run_cli_command(args)
                result['credential_type'] = json.loads(output)
                result['msg'] = f"Retrieved credential type {module.params['uuid']}"
                
                # Update if name is provided
                if module.params.get('name'):
                    args = cli_base + ['update', '--uuid', module.params['uuid'], 
                                     '--name', module.params['name'], '--format', 'json']
                    output = run_cli_command(args)
                    result['changed'] = True
                    result['msg'] = f"Updated credential type {module.params['uuid']}"
                    
                    # Get updated credential type
                    args = cli_base + ['get', '--uuid', module.params['uuid'], '--format', 'json']
                    output = run_cli_command(args)
                    result['credential_type'] = json.loads(output)
                    
            else:
                # List all credential types if no specific identifier
                args = cli_base + ['list', '--format', 'json']
                output = run_cli_command(args)
                result['credential_type'] = json.loads(output)
                result['msg'] = "Retrieved credential type list"
                
        elif state == 'import':
            if not module.params.get('file'):
                module.fail_json(msg="file parameter is required for import operation")
            
            if module.check_mode:
                result['msg'] = f"Would import credential type from {module.params['file']}"
                result['changed'] = True
            else:
                args = cli_base + ['import-json', '--file', module.params['file'], '--format', 'json']
                output = run_cli_command(args)
                result['credential_type'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Imported credential type from {module.params['file']}"
                
        elif state == 'export':
            if not module.params.get('file'):
                module.fail_json(msg="file parameter is required for export operation")
            if not (module.params.get('credential_type_id') or module.params.get('uuid')):
                module.fail_json(msg="credential_type_id or uuid is required for export operation")
            
            if module.check_mode:
                result['msg'] = f"Would export credential type to {module.params['file']}"
                result['changed'] = True
            else:
                args = cli_base + ['export-json', '--file', module.params['file'], '--format', 'json']
                if module.params.get('credential_type_id'):
                    args.extend(['--id', str(module.params['credential_type_id'])])
                elif module.params.get('uuid'):
                    args.extend(['--uuid', module.params['uuid']])
                    
                output = run_cli_command(args)
                result['credential_type'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Exported credential type to {module.params['file']}"
                
        elif state == 'validate':
            if not module.params.get('file'):
                module.fail_json(msg="file parameter is required for validate operation")
                
            args = cli_base + ['validate-json', '--file', module.params['file'], '--format', 'json']
            output = run_cli_command(args)
            result['credential_type'] = json.loads(output)
            result['msg'] = f"Validated credential type file {module.params['file']}"
            
        elif state == 'remove-json':
            if not module.params.get('file'):
                module.fail_json(msg="file parameter is required for remove-json operation")
                
            if module.check_mode:
                result['msg'] = f"Would remove credential type based on {module.params['file']}"
                result['changed'] = True
            else:
                args = cli_base + ['remove-json', '--file', module.params['file'], '--format', 'json']
                output = run_cli_command(args)
                result['credential_type'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Removed credential type based on {module.params['file']}"
                
        elif state == 'absent':
            module.fail_json(msg="Direct deletion by ID/UUID is not supported. Use remove-json with a file instead.")
            
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
