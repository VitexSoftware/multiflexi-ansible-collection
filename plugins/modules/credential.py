#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: credential
short_description: Manage credentials in Multiflexi

description:
    - This module allows you to get and update credentials in Multiflexi via CLI with idempotency logic.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the credential.
        required: true
        type: str
        choices: ['present', 'get']
    credential_id:
        description:
            - The ID of the credential.
        required: false
        type: int
    token:
        description:
            - User's access token (for get/update by token).
        required: false
        type: str
    company_id:
        description:
            - The company ID for the credential.
        required: false
        type: int
    name:
        description:
            - Name of the credential.
        required: false
        type: str
    type:
        description:
            - Type of the credential.
        required: false
        type: str
    value:
        description:
            - Value of the credential.
        required: false
        type: str
    multiflexi_cli:
        description:
            - Path to multiflexi-cli binary (default: multiflexi-cli in PATH).
        required: false
        type: str
        default: multiflexi-cli
"""

EXAMPLES = """
- name: Get a credential by ID
  credential:
    state: get
    credential_id: 1

- name: List all credentials
  credential:
    state: get

- name: Update a credential
  credential:
    state: present
    credential_id: 1
    name: "API Key"
    value: "newvalue"
"""

RETURN = """
credential:
    description: The credential object or list of credentials.
    type: dict or list
    returned: always
"""

def run_cli(module, args):
    cli = module.params.get('multiflexi_cli', 'multiflexi-cli')
    cmd = [cli] + args + ['--verbose', '--output', 'json']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        try:
            err = json.loads(e.stdout or e.stderr)
        except Exception:
            err = e.stdout or e.stderr
        module.fail_json(msg=f"CLI error: {err}", rc=e.returncode)
    except Exception as e:
        module.fail_json(msg=f"Failed to run CLI: {e}")

def find_existing_credential(module):
    # Priority: credential_id > token > name
    cli_args = []
    if module.params.get('credential_id'):
        cli_args = ['credential', 'get', '--id', str(module.params['credential_id'])]
    elif module.params.get('token'):
        cli_args = ['credential', 'get', '--token', module.params['token']]
    elif module.params.get('name'):
        cli_args = ['credential', 'get', '--name', module.params['name']]
    else:
        return None
    res = run_cli(module, cli_args)
    if isinstance(res, dict) and res.get('id'):
        return res
    return None

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'get']),
        credential_id=dict(type='int', required=False),
        token=dict(type='str', required=False),
        company_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        type=dict(type='str', required=False),
        value=dict(type='str', required=False),
        multiflexi_cli=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        credential=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']

    if state == 'get':
        # Try most specific identifier first
        cred = find_existing_credential(module)
        if cred:
            result['credential'] = cred
        else:
            # List all
            res = run_cli(module, ['credential', 'list'])
            result['credential'] = res
        module.exit_json(**result)

    elif state == 'present':
        cred = find_existing_credential(module)
        if not cred:
            module.fail_json(msg="Credential not found. Creation is not supported via CLI.")
        # Prepare update args (only supported fields)
        update_args = ['credential', 'update', '--id', str(cred['id'])]
        for field in ['token', 'company_id', 'name', 'type', 'value']:
            val = module.params.get(field)
            if val is not None:
                update_args += [f'--{field.replace("_", "-")}', str(val)]
        if module.check_mode:
            result['changed'] = True
            result['credential'] = cred
            module.exit_json(**result)
        run_cli(module, update_args)
        # Fetch latest
        latest = run_cli(module, ['credential', 'get', '--id', str(cred['id'])])
        result['changed'] = True
        result['credential'] = latest
        module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")

def main():
    run_module()

if __name__ == '__main__':
    main()
