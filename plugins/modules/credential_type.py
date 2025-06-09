#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = """
---
module: credential_type
short_description: Manage credential types in Multiflexi

description:
    - This module allows you to get, update, and list credential types in Multiflexi via REST API.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the credential type.
        required: true
        type: str
        choices: ['present', 'get']
    credential_type_id:
        description:
            - The ID of the credential type.
        required: false
        type: int
    name:
        description:
            - Name of the credential type.
        required: false
        type: str
    description:
        description:
            - Description of the credential type.
        required: false
        type: str
    url:
        description:
            - URL for the credential type.
        required: false
        type: str
    logo:
        description:
            - Logo URL for the credential type.
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
- name: Get a credential type by ID
  credential_type:
    state: get
    credential_type_id: 1
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: List all credential types
  credential_type:
    state: get
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: Update a credential type
  credential_type:
    state: present
    credential_type_id: 1
    name: "API Key"
    description: "API Key type"
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"
"""

RETURN = """
credential_type:
    description: The credential type object or list of credential types.
    type: dict or list
    returned: always
"""

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'get']),
        credential_type_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        url=dict(type='str', required=False),
        logo=dict(type='str', required=False),
        api_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
        credential_type=None
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
        if module.params['credential_type_id']:
            url = f"{api_url}/credential_type/{module.params['credential_type_id']}.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['credential_type'] = resp.json()
        else:
            url = f"{api_url}/credential_types.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['credential_type'] = resp.json()
        module.exit_json(**result)
    elif module.params['state'] == 'present':
        if not module.params['credential_type_id']:
            module.fail_json(msg="credential_type_id required for update")
        url = f"{api_url}/credential_type/{module.params['credential_type_id']}.{suffix}"
        data = {k: v for k, v in module.params.items() if k in [
            'name', 'description', 'url', 'logo'
        ] and v is not None}
        resp = requests.post(url, auth=auth, headers=headers, json=data)
        result['changed'] = True
        result['credential_type'] = resp.json()
        module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")

def main():
    run_module()

if __name__ == '__main__':
    main()
