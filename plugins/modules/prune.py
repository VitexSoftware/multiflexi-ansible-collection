#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: prune
short_description: Prune logs and jobs in MultiFlexi

description:
    - This module allows you to prune logs and jobs in MultiFlexi, keeping only the latest N records.
    - Helps maintain database performance by cleaning up old data.

author:
    - Vitex (@Vitexus)

options:
    logs:
        description:
            - Whether to prune the logs table.
        required: false
        type: bool
        default: false
    jobs:
        description:
            - Whether to prune the jobs table.
        required: false
        type: bool
        default: false
    keep:
        description:
            - Number of records to keep.
        required: false
        type: int
        default: 1000
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: Prune logs and jobs, keeping latest 500 records
  prune:
    logs: true
    jobs: true
    keep: 500

- name: Prune only logs, keeping default 1000 records
  prune:
    logs: true

- name: Prune only jobs with custom keep count
  prune:
    jobs: true
    keep: 2000
"""

RETURN = """
prune_result:
    description: Result of the pruning operation.
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
        logs=dict(type='bool', required=False, default=False),
        jobs=dict(type='bool', required=False, default=False),
        keep=dict(type='int', required=False, default=1000),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        prune_result=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'prune']

    # Check if at least one of logs or jobs is specified
    if not (module.params['logs'] or module.params['jobs']):
        module.fail_json(msg="At least one of 'logs' or 'jobs' must be true")

    try:
        args = cli_base.copy()
        
        if module.params['logs']:
            args.append('--logs')
        if module.params['jobs']:
            args.append('--jobs')
        
        args.extend(['--keep', str(module.params['keep'])])

        if module.check_mode:
            prune_targets = []
            if module.params['logs']:
                prune_targets.append('logs')
            if module.params['jobs']:
                prune_targets.append('jobs')
            
            result['msg'] = f"Would prune {', '.join(prune_targets)}, keeping {module.params['keep']} records"
            result['changed'] = True
        else:
            output = run_cli_command(args)
            # Try to parse as JSON, fall back to plain text if it fails
            try:
                result['prune_result'] = json.loads(output)
            except json.JSONDecodeError:
                result['prune_result'] = {"output": output.strip()}
            
            result['changed'] = True
            
            prune_targets = []
            if module.params['logs']:
                prune_targets.append('logs')
            if module.params['jobs']:
                prune_targets.append('jobs')
            
            result['msg'] = f"Pruned {', '.join(prune_targets)}, kept {module.params['keep']} records"
            
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()