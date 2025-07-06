#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>


DOCUMENTATION = """
---
module: application

short_description: Manage applications in Multiflexi

description:
    - This module allows you to create, update, get, and delete applications in Multiflexi using the multiflexi-cli.

author:
    - Vitex (@Vitexus)

version_added: "2.1.0"

options:
    state:
        description:
            - The state of the application.
        required: false
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
"""

EXAMPLES = """
    - name: Assign application to company
      vitexus.multiflexi.application:
        state: present
        name: ExampleApp
        executable: example.exe
        tags: ['tag1', 'tag2']
        status: active

    - name: Remove application from company
      vitexus.multiflexi.application:
        state: absent
        app_id: 123

    - name: Get application details
      vitexus.multiflexi.application:
        state: get
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


def run_cli_command(args, module=None, allow_not_found=False):
    if module and module._verbosity >= 2:
        module.warn(f"Running CLI command: {' '.join(args)}")
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        if module and module._verbosity >= 2:
            module.warn(f"CLI stdout: {result.stdout.strip()}")
            if result.stderr.strip():
                module.warn(f"CLI stderr: {result.stderr.strip()}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if hasattr(e, 'stdout') and e.stdout else ''
        stderr = e.stderr.strip() if hasattr(e, 'stderr') and e.stderr else ''
        if module and module._verbosity >= 2:
            module.warn(f"CLI error: {stderr}")
            if stdout:
                module.warn(f"CLI stdout (on error): {stdout}")
        try:
            if stdout:
                data = json.loads(stdout)
                if allow_not_found and isinstance(data, dict) and data.get('status') == 'not found':
                    return stdout
                if isinstance(data, dict) and data.get('message'):
                    raise Exception(f"multiflexi-cli error: {data.get('message')}")
        except Exception:
            pass
        raise Exception(f"multiflexi-cli error: {stderr or stdout or str(e)}")


def run_module():
    module_args = dict(
        state=dict(type='str', required=False, choices=['present', 'absent', 'get']),
        app_id=dict(type='int', required=False),
        uuid=dict(type='str', required=False),
        name=dict(type='str', required=False),
        executable=dict(type='str', required=False),
        tags=dict(type='list', elements='str', required=False),
        description=dict(type='str', required=False),
        appversion=dict(type='str', required=False),
        homepage=dict(type='str', required=False),  # <-- ensure homepage is present
        logo=dict(type='str', required=False),
        ociimage=dict(type='str', required=False),
        requirements=dict(type='str', required=False),
        json=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        app=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params.get('state')
    cli_base = ['multiflexi-cli', 'application']

    try:
        # If no state is provided, default to info/read (get)
        if not state or state == 'get':
            if module.params.get('app_id'):
                args = cli_base + ['get', '--id', str(module.params['app_id']), '--format', 'json', '--verbose']
            elif module.params.get('uuid'):
                args = cli_base + ['get', '--uuid', module.params['uuid'], '--format', 'json', '--verbose']
            elif module.params.get('name'):
                args = cli_base + ['get', '--name', module.params['name'], '--format', 'json', '--verbose']
            else:
                module.fail_json(msg='Either app_id, uuid, or name is required to get application info.')
            output = run_cli_command(args, module=module, allow_not_found=True)
            app = json.loads(output)
            if isinstance(app, dict) and app.get('status') == 'not found':
                result['app'] = None
            else:
                result['app'] = app
            module.exit_json(**result)
        elif state == 'present':
            # 1. Check for existing application by app_id > uuid > name
            found_app_id = None
            app_data = None
            if module.params.get('app_id'):
                check_args = cli_base + ['get', '--id', str(module.params['app_id']), '--format', 'json', '--verbose']
                output = run_cli_command(check_args, module=module, allow_not_found=True)
                app = json.loads(output)
                if app and isinstance(app, dict) and app.get('id') and app.get('status') != 'not found':
                    found_app_id = app['id']
                    app_data = app
            elif module.params.get('uuid'):
                check_args = cli_base + ['get', '--uuid', module.params['uuid'], '--format', 'json', '--verbose']
                output = run_cli_command(check_args, module=module, allow_not_found=True)
                app = json.loads(output)
                if app and isinstance(app, dict) and app.get('id') and app.get('status') != 'not found':
                    found_app_id = app['id']
                    app_data = app
            elif module.params.get('name'):
                check_args = cli_base + ['get', '--name', module.params['name'], '--format', 'json', '--verbose']
                output = run_cli_command(check_args, module=module, allow_not_found=True)
                app = json.loads(output)
                if app and isinstance(app, dict) and app.get('id') and app.get('status') != 'not found':
                    found_app_id = app['id']
                    app_data = app
            # Idempotency: Only update if any property differs
            needs_update = False
            for param in ['name', 'executable', 'description', 'uuid', 'homepage', 'logo', 'tags', 'appversion', 'ociimage', 'requirements', 'json']:
                value = module.params.get(param)
                if value is not None and app_data is not None:
                    app_val = app_data.get(param)
                    if param == 'tags':
                        # Compare tags as sets if both are present
                        if app_val is not None and set(value) != set(app_val):
                            needs_update = True
                    elif value != app_val:
                        needs_update = True
            # Build args for create/update
            def build_args(base, params):
                args = base[:]
                for param in ['name', 'executable', 'description', 'uuid', 'homepage', 'logo', 'appversion', 'ociimage', 'requirements', 'json']:
                    value = module.params.get(param)
                    if value is not None:
                        args += [f'--{param}', str(value)]
                if module.params.get('tags'):
                    args += ['--topics', ','.join(module.params['tags'])]
                args += ['--format', 'json', '--verbose']
                return args
            if found_app_id:
                if needs_update:
                    args = build_args(cli_base + ['update', '--id', str(found_app_id)], module.params)
                    run_cli_command(args, module=module)
                    result['changed'] = True
                else:
                    result['changed'] = False
            else:
                args = build_args(cli_base + ['create'], module.params)
                run_cli_command(args, module=module)
                result['changed'] = True
            # Always read the record and return as result
            if found_app_id:
                read_args = cli_base + ['get', '--id', str(found_app_id), '--format', 'json', '--verbose']
            elif module.params.get('uuid'):
                read_args = cli_base + ['get', '--uuid', module.params['uuid'], '--format', 'json', '--verbose']
            elif module.params.get('name'):
                read_args = cli_base + ['get', '--name', module.params['name'], '--format', 'json', '--verbose']
            else:
                module.fail_json(msg='Either app_id, uuid, or name is required to get application info.')
            output = run_cli_command(read_args, module=module, allow_not_found=True)
            app = json.loads(output)
            if isinstance(app, dict) and app.get('status') == 'not found':
                result['app'] = None
            else:
                result['app'] = app
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
                module.exit_json(**result)
            run_cli_command(args, module=module)
            result['changed'] = True
            # Optionally, try to get the deleted app info (should be not found)
            module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))


def main():
    run_module()


if __name__ == '__main__':
    main()
