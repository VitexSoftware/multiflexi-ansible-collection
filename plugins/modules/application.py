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
import requests


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

    headers = {'Content-Type': 'application/json'}
    auth = (module.params['username'], module.params['password'])
    api_url = module.params['api_url']
    suffix = 'json'

    if module.params['state'] == 'get':
        if module.params['app_id']:
            url = f"{api_url}/app/{module.params['app_id']}.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['app'] = resp.json()
        else:
            url = f"{api_url}/apps.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['app'] = resp.json()
        module.exit_json(**result)
    elif module.params['state'] == 'present':
        data = {k: v for k, v in module.params.items() if k in ['app_id', 'name', 'executable', 'tags', 'status'] and v is not None}
        url = f"{api_url}/app/"
        resp = requests.post(url, auth=auth, headers=headers, json=data)
        result['changed'] = True
        result['app'] = resp.json()
        module.exit_json(**result)
    elif module.params['state'] == 'absent':
        # No DELETE endpoint in OpenAPI, so just simulate
        result['changed'] = False
        result['message'] = 'Delete not implemented in API.'
        module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")


def main():
    run_module()


if __name__ == '__main__':
    main()
