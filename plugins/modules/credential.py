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
    - This module allows you to manage credentials in Multiflexi via CLI with idempotency logic.
    - Supports create, update, delete, get, and list operations.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the credential.
        required: true
        type: str
        choices: ['present', 'absent', 'get']
    credential_id:
        description:
            - The ID of the credential.
        required: false
        type: int
    name:
        description:
            - Name of the credential.
        required: false
        type: str
    company_id:
        description:
            - The company ID for the credential.
        required: false
        type: int
    credential_type_id:
        description:
            - The credential type ID.
        required: false
        type: int
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

- name: Create a new credential
  credential:
    state: present
    name: "API Key"
    company_id: 1
    credential_type_id: 1

- name: Update a credential
  credential:
    state: present
    credential_id: 1
    name: "Updated API Key"

- name: Delete a credential
  credential:
    state: absent
    credential_id: 1
"""

RETURN = """
credential:
    description: The credential object or list of credentials.
    type: dict or list
    returned: always
"""

def run_cli(module, args):
    cli = module.params.get('multiflexi_cli', 'multiflexi-cli')
    cmd = [cli] + args + ['--verbose', '--format', 'json']
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
    # Priority: credential_id > name
    if module.params.get('credential_id'):
        try:
            cli_args = ['credential', 'get', '--id', str(module.params['credential_id'])]
            res = run_cli(module, cli_args)
            if isinstance(res, dict) and res.get('id'):
                return res
        except Exception:
            return None
    elif module.params.get('name'):
        try:
            # List all credentials and find by name
            res = run_cli(module, ['credential', 'list'])
            if isinstance(res, list):
                for cred in res:
                    if cred.get('name') == module.params['name']:
                        return cred
        except Exception:
            return None
    return None

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'absent', 'get']),
        credential_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        company_id=dict(type='int', required=False),
        credential_type_id=dict(type='int', required=False),
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
            # Create new credential
            if not module.params.get('name'):
                module.fail_json(msg="Name is required for creating a new credential")
            if not module.params.get('company_id'):
                module.fail_json(msg="Company ID is required for creating a new credential")
            if not module.params.get('credential_type_id'):
                module.fail_json(msg="Credential type ID is required for creating a new credential")
            
            create_args = ['credential', 'create', '--name', module.params['name']]
            create_args += ['--company-id', str(module.params['company_id'])]
            create_args += ['--credential-type-id', str(module.params['credential_type_id'])]
            
            if module.check_mode:
                result['changed'] = True
                result['credential'] = {'name': module.params['name']}
                module.exit_json(**result)
            
            run_cli(module, create_args)
            # Find the newly created credential
            cred = find_existing_credential(module)
            result['changed'] = True
            result['credential'] = cred
            module.exit_json(**result)
        else:
            # Update existing credential
            update_args = ['credential', 'update', '--id', str(cred['id'])]
            changed = False
            
            for field, cli_arg in [('name', '--name'), ('company_id', '--company-id'), ('credential_type_id', '--credential-type-id')]:
                val = module.params.get(field)
                if val is not None and str(val) != str(cred.get(field.replace('_', '-').replace('credential-type-id', 'credential_type_id') if field == 'credential_type_id' else field, '')):
                    update_args += [cli_arg, str(val)]
                    changed = True
            
            if not changed:
                result['credential'] = cred
                module.exit_json(**result)
            
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
    
    elif state == 'absent':
        cred = find_existing_credential(module)
        if not cred:
            result['credential'] = None
            module.exit_json(**result)
        
        if module.check_mode:
            result['changed'] = True
            result['credential'] = None
            module.exit_json(**result)
        
        run_cli(module, ['credential', 'remove', '--id', str(cred['id'])])
        result['changed'] = True
        result['credential'] = None
        module.exit_json(**result)
    
    else:
        module.fail_json(msg="Invalid state")

def main():
    run_module()

if __name__ == '__main__':
    main()
