#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: queue
short_description: Manage job queues in MultiFlexi

description:
    - This module allows you to manage job queues in MultiFlexi.
    - Supports listing queue status and truncating the queue.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired action on the queue.
        required: true
        type: str
        choices: ['list', 'truncate']
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: List queue status
  queue:
    state: list

- name: Truncate the job queue
  queue:
    state: truncate
"""

RETURN = """
queue:
    description: Queue information or truncation result.
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
        state=dict(type='str', required=True, choices=['list', 'truncate']),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        queue=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'queue']

    try:
        if state == 'list':
            args = cli_base + ['list', '--format', 'json']
            output = run_cli_command(args)
            result['queue'] = json.loads(output)
            result['msg'] = "Retrieved queue status"
            
        elif state == 'truncate':
            if module.check_mode:
                result['msg'] = "Would truncate the job queue"
                result['changed'] = True
            else:
                args = cli_base + ['truncate', '--format', 'json']
                output = run_cli_command(args)
                result['queue'] = json.loads(output)
                result['changed'] = True
                result['msg'] = "Truncated job queue"
            
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()