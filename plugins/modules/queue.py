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
        required: false
        type: str
        choices: ['list', 'truncate', 'fix', 'overview']
        default: 'overview'
    limit:
        description:
            - Limit number of results for list action.
        required: false
        type: int
    order:
        description:
            - Sort order field.
        required: false
        type: str
    direction:
        description:
            - Sort direction.
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
- name: List queue status
  queue:
    state: list

- name: Fix the job queue
  queue:
    state: fix

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
        state=dict(type='str', required=False, default='overview', choices=['list', 'truncate', 'fix', 'overview']),
        limit=dict(type='int', required=False),
        order=dict(type='str', required=False),
        direction=dict(type='str', required=False),
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
        if state == 'overview':
            args = cli_base + ['--format', 'json']
            output = run_cli_command(args)
            result['queue'] = json.loads(output)
            result['msg'] = "Retrieved queue overview"
            
        elif state == 'list':
            args = cli_base + ['list', '--format', 'json']
            if module.params.get('limit'):
                args.extend(['--limit', str(module.params['limit'])])
            if module.params.get('order'):
                args.extend(['--order', module.params['order']])
            if module.params.get('direction'):
                args.extend(['--direction', module.params['direction']])
            output = run_cli_command(args)
            result['queue'] = json.loads(output)
            result['msg'] = "Retrieved queue status"
            
        elif state == 'fix':
            if module.check_mode:
                result['msg'] = "Would fix the job queue"
                result['changed'] = True
            else:
                args = cli_base + ['fix', '--format', 'json']
                output = run_cli_command(args)
                result['queue'] = json.loads(output)
                result['changed'] = True
                result['msg'] = "Fixed job queue"

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