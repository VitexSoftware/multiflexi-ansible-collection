#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests

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

    headers = {'Content-Type': 'application/json'}
    auth = (module.params['username'], module.params['password_api'])
    api_url = module.params['api_url']
    suffix = 'json'

    if module.params['state'] == 'get':
        if module.params['user_id']:
            url = f"{api_url}/user/{module.params['user_id']}.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['user'] = resp.json()
        else:
            url = f"{api_url}/users.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['user'] = resp.json()
        module.exit_json(**result)
    elif module.params['state'] == 'present':
        data = {k: v for k, v in module.params.items() if k in [
            'user_id', 'enabled', 'settings', 'email', 'firstname', 'lastname',
            'password', 'login'
        ] and v is not None}
        url = f"{api_url}/user/"
        resp = requests.post(url, auth=auth, headers=headers, json=data)
        result['changed'] = True
        result['user'] = resp.json()
        module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")

def main():
    run_module()

if __name__ == '__main__':
    main()
