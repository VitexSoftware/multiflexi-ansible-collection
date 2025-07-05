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
        choices: ['present', 'get']
    credential_type_id:
        description:
            - The ID of the credential type.
        required: false
        type: int
    name:
        description:
            - Name of the credential type.
        required: false
        type: str
    description:
        description:
            - Description of the credential type.
        required: false
        type: str
    url:
        description:
            - URL for the credential type.
        required: false
        type: str
    logo:
        description:
            - Logo URL for the credential type.
        required: false
        type: str
    api_url:
        description:
            - API base URL.
        required: true
        type: str
    username:
        description:
            - API username.
        required: true
        type: str
    password:
        description:
            - API password.
        required: true
        type: str
        no_log: true

"""

EXAMPLES = """
- name: Get a credential type by ID
  credential_type:
    state: get
    credential_type_id: 1
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: List all credential types
  credential_type:
    state: get
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: Update a credential type
  credential_type:
    state: present
    credential_type_id: 1
    name: "API Key"
    description: "API Key type"
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"
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
        state=dict(type='str', required=True, choices=['present', 'get']),
        credential_type_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        url=dict(type='str', required=False),
        logo=dict(type='str', required=False),
        api_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
        credential_type=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_base = ['multiflexi-cli', 'credtype']

    try:
        if state == 'get':
            # Use the most specific identifier: credential_type_id > name
            if module.params.get('credential_type_id'):
                args = cli_base + ['get', '--id', str(module.params['credential_type_id']), '--verbose', '--output', 'json']
            elif module.params.get('name'):
                args = cli_base + ['get', '--name', module.params['name'], '--verbose', '--output', 'json']
            else:
                args = cli_base + ['list', '--verbose', '--output', 'json']
            output = run_cli_command(args)
            result['credential_type'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'present':
            # 1. Check for existing credential type by id > name
            found_id = None
            if module.params.get('credential_type_id'):
                check_args = cli_base + ['get', '--id', str(module.params['credential_type_id']), '--verbose', '--output', 'json']
                output = run_cli_command(check_args)
                cred = json.loads(output)
                if cred and isinstance(cred, dict) and cred.get('id'):
                    found_id = cred['id']
            elif module.params.get('name'):
                check_args = cli_base + ['list', '--verbose', '--output', 'json', '--name', module.params['name']]
                output = run_cli_command(check_args)
                creds = json.loads(output)
                if creds and isinstance(creds, list) and len(creds) > 0:
                    found_id = creds[0].get('id')
            # 2. Create or update (CLI may not support create, so only update if found)
            if found_id:
                args = cli_base + ['update', '--id', str(found_id)]
                result['changed'] = True
                for param in ['name', 'description', 'url', 'logo']:
                    value = module.params.get(param)
                    if value is not None:
                        args += [f'--{param}', str(value)]
                args += ['--verbose', '--output', 'json']
                run_cli_command(args)
            else:
                module.fail_json(msg="Credential type not found for update. Use the UI or API to create new credential types.")
            # 3. Always read the record and return as result
            if found_id:
                read_args = cli_base + ['get', '--id', str(found_id), '--verbose', '--output', 'json']
            elif module.params.get('name'):
                read_args = cli_base + ['get', '--name', module.params['name'], '--verbose', '--output', 'json']
            else:
                read_args = cli_base + ['list', '--verbose', '--output', 'json']
            output = run_cli_command(read_args)
            result['credential_type'] = json.loads(output)
            module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))

def main():
    run_module()

if __name__ == '__main__':
    main()
