#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: job
short_description: Manage jobs in Multiflexi via multiflexi-cli

description:
    - This module allows you to create, update, get, and list jobs in Multiflexi using the multiflexi-cli tool.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the job.
        required: true
        type: str
        choices: ['present', 'get']
    job_id:
        description:
            - The ID of the job.
        required: false
        type: int
    app_id:
        description:
            - The ID of the application.
        required: false
        type: int
    runtemplate_id:
        description:
            - RunTemplate ID.
        required: false
        type: int
    scheduled:
        description:
            - Scheduled datetime.
        required: false
        type: str
    executor:
        description:
            - Executor type.
        required: false
        type: str
    schedule_type:
        description:
            - Schedule type.
        required: false
        type: str

"""

EXAMPLES = """
- name: Create or update a job
  job:
    state: present
    app_id: 1
    runtemplate_id: 2
    scheduled: "2025-06-17T10:00:00"
    executor: "shell"
    schedule_type: "once"

- name: Get a job by ID
  job:
    state: get
    job_id: 1

- name: List all jobs
  job:
    state: get
"""

RETURN = """
job:
    description: The job object or list of jobs.
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
        job_id=dict(type='int', required=False),
        app_id=dict(type='int', required=False),
        runtemplate_id=dict(type='int', required=False),
        scheduled=dict(type='str', required=False),
        executor=dict(type='str', required=False),
        schedule_type=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        job=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_base = ['multiflexi-cli', 'job']

    try:
        if state == 'get':
            if module.params['job_id']:
                args = cli_base + ['get', '--id', str(module.params['job_id']), '--format', 'json']
                output = run_cli_command(args)
                result['job'] = json.loads(output)
            else:
                args = cli_base + ['list', '--format', 'json']
                output = run_cli_command(args)
                result['job'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'present':
            # If job_id is provided, update; else, create
            if module.params['job_id']:
                args = cli_base + ['update', '--id', str(module.params['job_id'])]
                result['changed'] = True
            else:
                args = cli_base + ['create']
                result['changed'] = True
            # Add optional parameters
            for param in ['app_id', 'runtemplate_id', 'scheduled', 'executor', 'schedule_type']:
                value = module.params.get(param)
                if value is not None:
                    args += [f'--{param}', str(value)]
            args += ['--format', 'json']
            output = run_cli_command(args)
            result['job'] = json.loads(output)
            module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))

def main():
    run_module()

if __name__ == '__main__':
    main()
