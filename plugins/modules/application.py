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
    uuid:
        description:
            - The UUID of the application.
        required: false
        type: str
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
        uuid=dict(type='str', required=False),
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
            # Use the most specific identifier: app_id > uuid > name
            if module.params.get('app_id'):
                args = cli_base + ['get', '--id', str(module.params['app_id']), '--format', 'json', '--verbose']
            elif module.params.get('uuid'):
                args = cli_base + ['get', '--uuid', module.params['uuid'], '--format', 'json', '--verbose']
            elif module.params.get('name'):
                args = cli_base + ['get', '--name', module.params['name'], '--format', 'json', '--verbose']
            else:
                args = cli_base + ['list', '--format', 'json', '--verbose']
            output = run_cli_command(args)
            result['app'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'present':
            # 1. Check for existing application by app_id > uuid > name
            found_app_id = None
            if module.params.get('app_id'):
                check_args = cli_base + ['get', '--id', str(module.params['app_id']), '--format', 'json', '--verbose']
                output = run_cli_command(check_args)
                app = json.loads(output)
                if app and isinstance(app, dict) and app.get('id'):
                    found_app_id = app['id']
            elif module.params.get('uuid'):
                check_args = cli_base + ['list', '--format', 'json', '--uuid', module.params['uuid'], '--verbose']
                output = run_cli_command(check_args)
                apps = json.loads(output)
                if apps and isinstance(apps, list) and len(apps) > 0:
                    found_app_id = apps[0].get('id')
            elif module.params.get('name'):
                check_args = cli_base + ['list', '--format', 'json', '--name', module.params['name'], '--verbose']
                output = run_cli_command(check_args)
                apps = json.loads(output)
                if apps and isinstance(apps, list) and len(apps) > 0:
                    found_app_id = apps[0].get('id')
            # 2. Create or update
            if found_app_id:
                args = cli_base + ['update', '--id', str(found_app_id)]
                result['changed'] = True
            else:
                args = cli_base + ['create']
                result['changed'] = True
            for param in ['name', 'executable', 'status', 'uuid']:
                value = module.params.get(param)
                if value is not None:
                    args += [f'--{param}', str(value)]
            if module.params.get('tags'):
                args += ['--topics', ','.join(module.params['tags'])]
            args += ['--format', 'json', '--verbose']
            run_cli_command(args)
            # 3. Always read the record and return as result
            if found_app_id:
                read_args = cli_base + ['get', '--id', str(found_app_id), '--format', 'json', '--verbose']
            elif module.params.get('uuid'):
                read_args = cli_base + ['get', '--uuid', module.params['uuid'], '--format', 'json', '--verbose']
            elif module.params.get('name'):
                read_args = cli_base + ['get', '--name', module.params['name'], '--format', 'json', '--verbose']
            else:
                read_args = cli_base + ['list', '--format', 'json', '--verbose']
            output = run_cli_command(read_args)
            result['app'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'absent':
            # Use the most specific identifier for removal
            if module.params.get('app_id'):
                args = cli_base + ['delete', '--id', str(module.params['app_id']), '--format', 'json', '--verbose']
            elif module.params.get('uuid'):
                args = cli_base + ['delete', '--uuid', module.params['uuid'], '--format', 'json', '--verbose']
            elif module.params.get('name'):
                args = cli_base + ['delete', '--name', module.params['name'], '--format', 'json', '--verbose']
            else:
                result['changed'] = False
                result['message'] = 'app_id, uuid, or name required for absent state.'
                module.exit_json(**result)
            output = run_cli_command(args)
            result['changed'] = True
            result['app'] = json.loads(output)
            module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))


def main():
    run_module()


if __name__ == '__main__':
    main()
