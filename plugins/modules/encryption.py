#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: encryption
short_description: Manage encryption keys in MultiFlexi

description:
    - This module allows you to manage encryption keys in MultiFlexi.
    - Supports checking encryption status and initializing encryption keys.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the encryption system.
        required: true
        type: str
        choices: ['status', 'init']
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: Check encryption status
  encryption:
    state: status

- name: Initialize encryption keys
  encryption:
    state: init
"""

RETURN = """
encryption:
    description: The encryption status information.
    type: dict
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
        state=dict(type='str', required=True, choices=['status', 'init']),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        encryption=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'encryption']

    try:
        if state == 'status':
            args = cli_base + ['status', '--format', 'json']
            output = run_cli_command(args)
            result['encryption'] = json.loads(output)
            result['msg'] = "Retrieved encryption status"
            
        elif state == 'init':
            if module.check_mode:
                result['msg'] = "Would initialize encryption keys"
                result['changed'] = True
            else:
                args = cli_base + ['init', '--format', 'json']
                output = run_cli_command(args)
                result['encryption'] = json.loads(output)
                result['changed'] = True
                result['msg'] = "Initialized encryption keys"
            
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()