#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = """
---
module: job
short_description: Manage jobs in Multiflexi

description:
    - This module allows you to create, update, get, and list jobs in Multiflexi via REST API.

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
    company_id:
        description:
            - The ID of the company.
        required: false
        type: int
    begin:
        description:
            - Start time.
        required: false
        type: str
    end:
        description:
            - End time.
        required: false
        type: str
    exitcode:
        description:
            - Exit code.
        required: false
        type: int
    stdout:
        description:
            - Stdout output.
        required: false
        type: str
    stderr:
        description:
            - Stderr output.
        required: false
        type: str
    launched_by:
        description:
            - Who launched the job.
        required: false
        type: str
    env:
        description:
            - Environment variables.
        required: false
        type: str
    command:
        description:
            - Command executed.
        required: false
        type: str
    schedule:
        description:
            - Schedule string.
        required: false
        type: str
    executor:
        description:
            - Executor type.
        required: false
        type: str
    runtemplate_id:
        description:
            - RunTemplate ID.
        required: false
        type: int
    app_version:
        description:
            - App version.
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
- name: Create or update a job
  job:
    state: present
    app_id: 1
    company_id: 1
    command: "ls -l"
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: Get a job by ID
  job:
    state: get
    job_id: 1
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: List all jobs
  job:
    state: get
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"
"""

RETURN = """
job:
    description: The job object or list of jobs.
    type: dict or list
    returned: always
"""

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'get']),
        job_id=dict(type='int', required=False),
        app_id=dict(type='int', required=False),
        company_id=dict(type='int', required=False),
        begin=dict(type='str', required=False),
        end=dict(type='str', required=False),
        exitcode=dict(type='int', required=False),
        stdout=dict(type='str', required=False),
        stderr=dict(type='str', required=False),
        launched_by=dict(type='str', required=False),
        env=dict(type='str', required=False),
        command=dict(type='str', required=False),
        schedule=dict(type='str', required=False),
        executor=dict(type='str', required=False),
        runtemplate_id=dict(type='int', required=False),
        app_version=dict(type='str', required=False),
        api_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
        job=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    headers = {'Content-Type': 'application/json'}
    auth = (module.params['username'], module.params['password'])
    api_url = module.params['api_url']
    suffix = 'json'

    if module.params['state'] == 'get':
        if module.params['job_id']:
            url = f"{api_url}/job/{module.params['job_id']}.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['job'] = resp.json()
        else:
            url = f"{api_url}/jobs.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['job'] = resp.json()
        module.exit_json(**result)
    elif module.params['state'] == 'present':
        data = {k: v for k, v in module.params.items() if k in [
            'job_id', 'app_id', 'company_id', 'begin', 'end', 'exitcode',
            'stdout', 'stderr', 'launched_by', 'env', 'command', 'schedule',
            'executor', 'runtemplate_id', 'app_version'
        ] and v is not None}
        url = f"{api_url}/job/"
        resp = requests.post(url, auth=auth, headers=headers, json=data)
        result['changed'] = True
        result['job'] = resp.json()
        module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")

def main():
    run_module()

if __name__ == '__main__':
    main()
