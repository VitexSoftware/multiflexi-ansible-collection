#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = """
---
module: credential
short_description: Manage credentials in Multiflexi

description:
    - This module allows you to get, update, and list credentials in Multiflexi via REST API.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the credential.
        required: true
        type: str
        choices: ['present', 'get']
    credential_id:
        description:
            - The ID of the credential.
        required: false
        type: int
    token:
        description:
            - User's access token (for get/update by token).
        required: false
        type: str
    company_id:
        description:
            - The company ID for the credential.
        required: false
        type: int
    name:
        description:
            - Name of the credential.
        required: false
        type: str
    type:
        description:
            - Type of the credential.
        required: false
        type: str
    value:
        description:
            - Value of the credential.
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
- name: Get a credential by ID
  credential:
    state: get
    credential_id: 1
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: List all credentials
  credential:
    state: get
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: Update a credential
  credential:
    state: present
    credential_id: 1
    name: "API Key"
    value: "newvalue"
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"
"""

RETURN = """
credential:
    description: The credential object or list of credentials.
    type: dict or list
    returned: always
"""

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'get']),
        credential_id=dict(type='int', required=False),
        token=dict(type='str', required=False),
        company_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        type=dict(type='str', required=False),
        value=dict(type='str', required=False),
        api_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
        credential=None
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
        if module.params['credential_id']:
            url = f"{api_url}/credential/{module.params['credential_id']}.{suffix}"
            params = {}
            if module.params['token']:
                params['token'] = module.params['token']
            resp = requests.get(url, auth=auth, headers=headers, params=params)
            result['credential'] = resp.json()
        else:
            url = f"{api_url}/credentials.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['credential'] = resp.json()
        module.exit_json(**result)
    elif module.params['state'] == 'present':
        if not module.params['credential_id']:
            module.fail_json(msg="credential_id required for update")
        url = f"{api_url}/credential/{module.params['credential_id']}.{suffix}"
        data = {k: v for k, v in module.params.items() if k in [
            'token', 'company_id', 'name', 'type', 'value'
        ] and v is not None}
        resp = requests.post(url, auth=auth, headers=headers, json=data)
        result['changed'] = True
        result['credential'] = resp.json()
        module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")

def main():
    run_module()

if __name__ == '__main__':
    main()
