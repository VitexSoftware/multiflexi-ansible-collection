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
            if module.params['user_id']:
                args = cli_base + ['get', '--id', str(module.params['user_id']), '--format', 'json']
                output = run_cli_command(args)
                result['user'] = json.loads(output)
            else:
                args = cli_base + ['list', '--format', 'json']
                output = run_cli_command(args)
                result['user'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'present':
            # If user_id is provided, update; else, create
            if module.params.get('user_id'):
                args = cli_base + ['update', '--id', str(module.params['user_id'])]
                result['changed'] = True
            else:
                args = cli_base + ['create']
                result['changed'] = True
            # Add optional parameters
            for param in ['enabled', 'settings', 'email', 'firstname', 'lastname', 'password', 'login']:
                value = module.params.get(param)
                if value is not None:
                    args += [f'--{param}', str(int(value)) if isinstance(value, bool) else str(value)]
            args += ['--format', 'json']
            output = run_cli_command(args)
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
