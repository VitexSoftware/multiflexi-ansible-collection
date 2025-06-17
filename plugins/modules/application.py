#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>


DOCUMENTATION = """
---
module: application

short_description: Manage applications in Multiflexi

description:
    - This module allows you to assign or remove applications to/from companies in Multiflexi.

author:
    - Vitex (@Vitexus)

requirements:
    - "python >= 3.9"

version_added: "2.1.0"

options:
    state:
        description:
            - The state of the application.
        required: true
        type: str
        choices: ['present', 'absent', 'get']
    app_id:
        description:
            - The ID of the application.
        required: false
        type: int
    name:
        description:
            - The name of the application.
        required: false
        type: str
    executable:
        description:
            - The executable of the application.
        required: false
        type: str
    tags:
        description:
            - The tags associated with the application.
        required: false
        type: list
        elements: str
    status:
        description:
            - The status of the application.
        required: false
        type: str
    api_url:
        description:
            - The base URL for the API.
        required: true
        type: str
    username:
        description:
            - The username for API authentication.
        required: true
        type: str
    password:
        description:
            - The password for API authentication.
        required: true
        type: str
"""

EXAMPLES = """
    - name: Assign application to company
      vitexus.multiflexi.application:
        state: present
        api_url: https://api.example.com
        username: myuser
        password: mypass
        name: ExampleApp
        executable: example.exe
        tags: ['tag1', 'tag2']
        status: active

    - name: Remove application from company
      vitexus.multiflexi.application:
        state: absent
        api_url: https://api.example.com
        username: myuser
        password: mypass
        app_id: 123

    - name: Get application details
      vitexus.multiflexi.application:
        state: get
        api_url: https://api.example.com
        username: myuser
        password: mypass
        app_id: 123
"""

RETURN = """
    message:
        description: The output message that the module generates.
        type: str
        returned: always
    changed:
        description: Whether the application was changed.
        type: bool
        returned: always
    app:
        description: The application data.
        type: dict
        returned: when state is present or get
"""


from ansible.module_utils.basic import AnsibleModule
import subprocess
import json


def run_cli_command(args):
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"multiflexi-cli error: {e.stderr.strip()}")


def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'absent', 'get']),
        app_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        executable=dict(type='str', required=False),
        tags=dict(type='list', elements='str', required=False),
        status=dict(type='str', required=False),
        api_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
        app=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_base = ['multiflexi-cli', 'application']

    try:
        if state == 'get':
            if module.params['app_id']:
                args = cli_base + ['get', '--id', str(module.params['app_id']), '--format', 'json']
                output = run_cli_command(args)
                result['app'] = json.loads(output)
            else:
                args = cli_base + ['list', '--format', 'json']
                output = run_cli_command(args)
                result['app'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'present':
            # If app_id is provided, update; else, create
            if module.params['app_id']:
                args = cli_base + ['update', '--id', str(module.params['app_id'])]
                result['changed'] = True
            else:
                args = cli_base + ['create']
                result['changed'] = True
            # Add optional parameters
            for param in ['name', 'executable', 'status']:
                value = module.params.get(param)
                if value is not None:
                    args += [f'--{param}', str(value)]
            # Handle tags as comma-separated string if provided
            if module.params.get('tags'):
                args += ['--topics', ','.join(module.params['tags'])]
            args += ['--format', 'json']
            output = run_cli_command(args)
            result['app'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'absent':
            if module.params['app_id']:
                args = cli_base + ['delete', '--id', str(module.params['app_id']), '--format', 'json']
                output = run_cli_command(args)
                result['changed'] = True
                result['app'] = json.loads(output)
                module.exit_json(**result)
            else:
                result['changed'] = False
                result['message'] = 'app_id required for absent state.'
                module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))


def main():
    run_module()


if __name__ == '__main__':
    main()
