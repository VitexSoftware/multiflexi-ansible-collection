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
    - This module allows you to create, update, get, and list jobs in Multiflexi using the multiflexi-cli tool with idempotency logic.

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
    multiflexi_cli:
        description:
            - Path to multiflexi-cli binary (default: multiflexi-cli in PATH).
        required: false
        type: str
        default: multiflexi-cli
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

def find_existing_job(module):
    # Priority: job_id > (app_id + runtemplate_id + scheduled)
    if module.params.get('job_id'):
        res = run_cli(module, ['job', 'get', '--id', str(module.params['job_id'])])
        if isinstance(res, dict) and res.get('id'):
            return res
    elif module.params.get('app_id') and module.params.get('runtemplate_id') and module.params.get('scheduled'):
        # Try to find by unique combination
        jobs = run_cli(module, ['job', 'list'])
        for job in jobs if isinstance(jobs, list) else []:
            if (str(job.get('app_id')) == str(module.params['app_id']) and
                str(job.get('runtemplate_id')) == str(module.params['runtemplate_id']) and
                str(job.get('scheduled')) == str(module.params['scheduled'])):
                return job
    return None

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'get']),
        job_id=dict(type='int', required=False),
        app_id=dict(type='int', required=False),
        runtemplate_id=dict(type='int', required=False),
        scheduled=dict(type='str', required=False),
        executor=dict(type='str', required=False),
        schedule_type=dict(type='str', required=False),
        multiflexi_cli=dict(type='str', required=False, default='multiflexi-cli'),
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

    if state == 'get':
        job = find_existing_job(module)
        if job:
            result['job'] = job
        else:
            jobs = run_cli(module, ['job', 'list'])
            result['job'] = jobs
        module.exit_json(**result)

    elif state == 'present':
        job = find_existing_job(module)
        if job:
            # Update
            update_args = ['job', 'update', '--id', str(job['id'])]
            for field in ['app_id', 'runtemplate_id', 'scheduled', 'executor', 'schedule_type']:
                val = module.params.get(field)
                if val is not None:
                    update_args += [f'--{field}', str(val)]
            if module.check_mode:
                result['changed'] = True
                result['job'] = job
                module.exit_json(**result)
            run_cli(module, update_args)
            latest = run_cli(module, ['job', 'get', '--id', str(job['id'])])
            result['changed'] = True
            result['job'] = latest
            module.exit_json(**result)
        else:
            # Create
            create_args = ['job', 'create']
            for field in ['app_id', 'runtemplate_id', 'scheduled', 'executor', 'schedule_type']:
                val = module.params.get(field)
                if val is not None:
                    create_args += [f'--{field}', str(val)]
            if module.check_mode:
                # Simulate creation
                result['changed'] = True
                result['job'] = None
                module.exit_json(**result)
            created = run_cli(module, create_args)
            # Fetch latest by id
            job_id = created.get('id')
            if job_id:
                latest = run_cli(module, ['job', 'get', '--id', str(job_id)])
                result['job'] = latest
            else:
                result['job'] = created
            result['changed'] = True
            module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")

def main():
    run_module()

if __name__ == '__main__':
    main()
