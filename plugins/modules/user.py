#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: user
short_description: Manage users in Multiflexi

description:
    - This module allows you to create, update, get, and list users in Multiflexi via REST API.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the user.
        required: true
        type: str
        choices: ['present', 'get']
    user_id:
        description:
            - The ID of the user.
        required: false
        type: int
    enabled:
        description:
            - Whether the user is enabled.
        required: false
        type: bool
    settings:
        description:
            - User settings.
        required: false
        type: str
    email:
        description:
            - Email address.
        required: false
        type: str
    firstname:
        description:
            - First name.
        required: false
        type: str
    lastname:
        description:
            - Last name.
        required: false
        type: str
    password:
        description:
            - Password.
        required: false
        type: str
    login:
        description:
            - Login name.
        required: false
        type: str

"""

EXAMPLES = """
- name: Create or update a user
  user:
    state: present
    email: "user@example.com"
    firstname: "John"
    lastname: "Doe"
    login: "jdoe"
    password: "secret"

- name: Get a user by ID
  user:
    state: get
    user_id: 1

- name: List all users
  user:
    state: get
"""

RETURN = """
user:
    description: The user object or list of users.
    type: dict or list
    returned: always
"""

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
        # If CLI returned JSON in stdout, try to parse and show message
        try:
            if stdout:
                data = json.loads(stdout)
                if allow_not_found and isinstance(data, dict) and data.get('status') == 'not found':
                    return stdout  # allow caller to handle not found
                if isinstance(data, dict) and data.get('message'):
                    raise Exception(f"multiflexi-cli error: {data.get('message')}")
        except Exception:
            pass
        raise Exception(f"multiflexi-cli error: {stderr or stdout or str(e)}")

def run_module():
    module_args = dict(
        state=dict(type='str', required=False, choices=['present', 'get']),
        user_id=dict(type='int', required=False),
        enabled=dict(type='bool', required=False),
        settings=dict(type='str', required=False),
        email=dict(type='str', required=False),
        firstname=dict(type='str', required=False),
        lastname=dict(type='str', required=False),
        password=dict(type='str', required=False),
        login=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        user=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params.get('state')
    cli_base = ['multiflexi-cli', 'user']

    try:
        # If no state is provided, default to info/read (get)
        if not state:
            # Use the most specific identifier: user_id > login > email
            if module.params.get('user_id'):
                args = cli_base + ['get', '--id', str(module.params['user_id']), '--format', 'json', '--verbose']
            elif module.params.get('login'):
                args = cli_base + ['get', '--login', module.params['login'], '--format', 'json', '--verbose']
            elif module.params.get('email'):
                args = cli_base + ['get', '--email', module.params['email'], '--format', 'json', '--verbose']
            else:
                args = cli_base + ['list', '--format', 'json', '--verbose']
            output = run_cli_command(args, module=module, allow_not_found=True)
            user = json.loads(output)
            if isinstance(user, dict) and user.get('status') == 'not found':
                result['user'] = None
            else:
                result['user'] = user
            module.exit_json(**result)
        elif state == 'get':
            # Use the most specific identifier: user_id > login > email
            if module.params.get('user_id'):
                args = cli_base + ['get', '--id', str(module.params['user_id']), '--format', 'json', '--verbose']
            elif module.params.get('login'):
                args = cli_base + ['get', '--login', module.params['login'], '--format', 'json', '--verbose']
            elif module.params.get('email'):
                args = cli_base + ['get', '--email', module.params['email'], '--format', 'json', '--verbose']
            else:
                args = cli_base + ['list', '--format', 'json', '--verbose']
            output = run_cli_command(args, module=module)
            result['user'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'present':
            # 1. Check for existing user by user_id > login > email
            found_user_id = None
            user_data = None
            if module.params.get('user_id'):
                check_args = cli_base + ['get', '--id', str(module.params['user_id']), '--format', 'json', '--verbose']
                output = run_cli_command(check_args, module=module, allow_not_found=True)
                user = json.loads(output)
                if user and isinstance(user, dict) and user.get('id') and user.get('status') != 'not found':
                    found_user_id = user['id']
                    user_data = user
            elif module.params.get('login'):
                check_args = cli_base + ['get', '--login', module.params['login'], '--format', 'json', '--verbose']
                output = run_cli_command(check_args, module=module, allow_not_found=True)
                user = json.loads(output)
                if user and isinstance(user, dict) and user.get('id') and user.get('status') != 'not found':
                    found_user_id = user['id']
                    user_data = user
            elif module.params.get('email'):
                check_args = cli_base + ['get', '--email', module.params['email'], '--format', 'json', '--verbose']
                output = run_cli_command(check_args, module=module, allow_not_found=True)
                user = json.loads(output)
                if user and isinstance(user, dict) and user.get('id') and user.get('status') != 'not found':
                    found_user_id = user['id']
                    user_data = user
            # 2. Idempotency: Only update if any property differs
            needs_update = False
            update_params = {}
            for param in ['enabled', 'settings', 'email', 'firstname', 'lastname', 'password', 'login']:
                value = module.params.get(param)
                if value is not None and user_data is not None:
                    # Password is never compared for idempotency
                    if param == 'password':
                        continue
                    # Compare bools and strings
                    user_val = user_data.get(param)
                    if isinstance(value, bool):
                        user_val = bool(user_val)
                    if value != user_val:
                        needs_update = True
                        update_params[param] = value
            if found_user_id:
                if needs_update or module.params.get('password') is not None:
                    args = cli_base + ['update', '--id', str(found_user_id)]
                    for param in ['enabled', 'settings', 'email', 'firstname', 'lastname', 'password', 'login']:
                        value = module.params.get(param)
                        if value is not None:
                            args += [f'--{param}', str(int(value)) if isinstance(value, bool) else str(value)]
                    args += ['--format', 'json']
                    try:
                        run_cli_command(args, module=module)
                        result['changed'] = True
                    except Exception as e:
                        module.fail_json(msg=f"Failed to update user: {str(e)}")
                else:
                    result['changed'] = False
            else:
                args = cli_base + ['create']
                for param in ['enabled', 'settings', 'email', 'firstname', 'lastname', 'password', 'login']:
                    value = module.params.get(param)
                    if value is not None:
                        args += [f'--{param}', str(int(value)) if isinstance(value, bool) else str(value)]
                args += ['--format', 'json']
                try:
                    run_cli_command(args, module=module)
                    result['changed'] = True
                except Exception as e:
                    module.fail_json(msg=f"Failed to create user: {str(e)}")
            # 3. Always read the record and return as result
            if found_user_id:
                read_args = cli_base + ['get', '--id', str(found_user_id), '--format', 'json', '--verbose']
            elif module.params.get('login'):
                read_args = cli_base + ['get', '--login', module.params['login'], '--format', 'json', '--verbose']
            elif module.params.get('email'):
                read_args = cli_base + ['get', '--email', module.params['email'], '--format', 'json', '--verbose']
            else:
                read_args = cli_base + ['list', '--format', 'json', '--verbose']
            output = run_cli_command(read_args, module=module)
            user = json.loads(output)
            if isinstance(user, dict) and user.get('status') == 'not found':
                result['user'] = None
            else:
                result['user'] = user
            module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))

def main():
    run_module()

if __name__ == '__main__':
    main()
