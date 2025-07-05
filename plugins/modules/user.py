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
    password_api:
        description:
            - API password.
        required: true
        type: str
        no_log: true

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
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password_api: "secret"

- name: Get a user by ID
  user:
    state: get
    user_id: 1
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password_api: "secret"

- name: List all users
  user:
    state: get
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password_api: "secret"
"""

RETURN = """
user:
    description: The user object or list of users.
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
        user_id=dict(type='int', required=False),
        enabled=dict(type='bool', required=False),
        settings=dict(type='str', required=False),
        email=dict(type='str', required=False),
        firstname=dict(type='str', required=False),
        lastname=dict(type='str', required=False),
        password=dict(type='str', required=False),
        login=dict(type='str', required=False),
        api_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password_api=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
        user=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_base = ['multiflexi-cli', 'user']

    try:
        if state == 'get':
            # Use the most specific identifier: user_id > login > email
            if module.params.get('user_id'):
                args = cli_base + ['get', '--id', str(module.params['user_id']), '--format', 'json', '--verbose']
            elif module.params.get('login'):
                args = cli_base + ['get', '--login', module.params['login'], '--format', 'json', '--verbose']
            elif module.params.get('email'):
                args = cli_base + ['get', '--email', module.params['email'], '--format', 'json', '--verbose']
            else:
                args = cli_base + ['list', '--format', 'json', '--verbose']
            output = run_cli_command(args)
            result['user'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'present':
            # 1. Check for existing user by user_id > login > email
            found_user_id = None
            if module.params.get('user_id'):
                check_args = cli_base + ['get', '--id', str(module.params['user_id']), '--format', 'json', '--verbose']
                output = run_cli_command(check_args)
                user = json.loads(output)
                if user and isinstance(user, dict) and user.get('id'):
                    found_user_id = user['id']
            elif module.params.get('login'):
                check_args = cli_base + ['list', '--format', 'json', '--login', module.params['login'], '--verbose']
                output = run_cli_command(check_args)
                users = json.loads(output)
                if users and isinstance(users, list) and len(users) > 0:
                    found_user_id = users[0].get('id')
            elif module.params.get('email'):
                check_args = cli_base + ['list', '--format', 'json', '--email', module.params['email'], '--verbose']
                output = run_cli_command(check_args)
                users = json.loads(output)
                if users and isinstance(users, list) and len(users) > 0:
                    found_user_id = users[0].get('id')
            # 2. Create or update
            if found_user_id:
                args = cli_base + ['update', '--id', str(found_user_id)]
                result['changed'] = True
            else:
                args = cli_base + ['create']
                result['changed'] = True
            for param in ['enabled', 'settings', 'email', 'firstname', 'lastname', 'password', 'login']:
                value = module.params.get(param)
                if value is not None:
                    args += [f'--{param}', str(int(value)) if isinstance(value, bool) else str(value)]
            args += ['--format', 'json']
            run_cli_command(args)
            # 3. Always read the record and return as result
            if found_user_id:
                read_args = cli_base + ['get', '--id', str(found_user_id), '--format', 'json', '--verbose']
            elif module.params.get('login'):
                read_args = cli_base + ['get', '--login', module.params['login'], '--format', 'json', '--verbose']
            elif module.params.get('email'):
                read_args = cli_base + ['get', '--email', module.params['email'], '--format', 'json', '--verbose']
            else:
                read_args = cli_base + ['list', '--format', 'json', '--verbose']
            output = run_cli_command(read_args)
            result['user'] = json.loads(output)
            module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))

def main():
    run_module()

if __name__ == '__main__':
    main()
