#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: token
short_description: Manage authentication tokens in MultiFlexi

description:
    - This module allows you to manage authentication tokens in MultiFlexi.
    - Supports listing, getting, creating, generating, and updating tokens.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the token.
        required: true
        type: str
        choices: ['present', 'absent', 'list', 'generate']
    token_id:
        description:
            - The ID of the token.
        required: false
        type: int
    user_id:
        description:
            - The user ID for the token.
        required: false
        type: int
    token_value:
        description:
            - The token value (for updates).
        required: false
        type: str
        no_log: true
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: List all tokens
  token:
    state: list

- name: Get a specific token by ID
  token:
    state: present
    token_id: 1

- name: Create a token for user
  token:
    state: present
    user_id: 3

- name: Generate a new token for user
  token:
    state: generate
    user_id: 2

- name: Update a token
  token:
    state: present
    token_id: 1
    token_value: "new-token-value"
"""

RETURN = """
token:
    description: The token object or list of tokens.
    type: dict or list
    returned: always
msg:
    description: A message describing the action taken.
    type: str
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
        state=dict(type='str', required=True, choices=['present', 'absent', 'list', 'generate']),
        token_id=dict(type='int', required=False),
        user_id=dict(type='int', required=False),
        token_value=dict(type='str', required=False, no_log=True),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        token=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'token']

    try:
        if state == 'list':
            args = cli_base + ['list', '--format', 'json']
            output = run_cli_command(args)
            result['token'] = json.loads(output)
            result['msg'] = "Retrieved token list"
            
        elif state == 'present':
            if module.params.get('token_id'):
                # Get existing token
                args = cli_base + ['get', '--id', str(module.params['token_id']), '--format', 'json']
                output = run_cli_command(args)
                existing_token = json.loads(output)
                
                if existing_token:
                    # Update existing token if token_value provided
                    if module.params.get('token_value'):
                        args = cli_base + ['update', '--id', str(module.params['token_id']), 
                                         '--token', module.params['token_value'], '--format', 'json']
                        output = run_cli_command(args)
                        result['changed'] = True
                        result['msg'] = f"Updated token {module.params['token_id']}"
                    else:
                        result['msg'] = f"Retrieved token {module.params['token_id']}"
                    
                    # Get updated token
                    args = cli_base + ['get', '--id', str(module.params['token_id']), '--format', 'json']
                    output = run_cli_command(args)
                    result['token'] = json.loads(output)
                else:
                    module.fail_json(msg=f"Token with ID {module.params['token_id']} not found")
                    
            elif module.params.get('user_id'):
                # Create new token for user
                args = cli_base + ['create', '--user', str(module.params['user_id']), '--format', 'json']
                if module.params.get('token_value'):
                    args.extend(['--token', module.params['token_value']])
                output = run_cli_command(args)
                result['token'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Created token for user {module.params['user_id']}"
            else:
                module.fail_json(msg="Either token_id or user_id is required for present state")
                
        elif state == 'generate':
            if not module.params.get('user_id'):
                module.fail_json(msg="user_id is required for generate state")
            
            args = cli_base + ['generate', '--user', str(module.params['user_id']), '--format', 'json']
            output = run_cli_command(args)
            result['token'] = json.loads(output)
            result['changed'] = True
            result['msg'] = f"Generated new token for user {module.params['user_id']}"
            
        elif state == 'absent':
            module.fail_json(msg="Token deletion is not supported by the CLI")
            
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()