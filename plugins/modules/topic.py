#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = """
---
module: topic
short_description: Manage topics in Multiflexi

description:
    - This module allows you to get, update, and list topics in Multiflexi via REST API.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the topic.
        required: true
        type: str
        choices: ['present', 'get']
    topic_id:
        description:
            - The ID of the topic.
        required: false
        type: int
    name:
        description:
            - Name of the topic.
        required: false
        type: str
    description:
        description:
            - Description of the topic.
        required: false
        type: str
    color:
        description:
            - Color of the topic.
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
- name: Get a topic by ID
  topic:
    state: get
    topic_id: 1
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: List all topics
  topic:
    state: get
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"

- name: Update a topic
  topic:
    state: present
    topic_id: 1
    name: "Important"
    color: "#ff0000"
    api_url: "https://demo.multiflexi.com/api/VitexSoftware/MultiFlexi/1.0.0"
    username: "admin"
    password: "secret"
"""

RETURN = """
topic:
    description: The topic object or list of topics.
    type: dict or list
    returned: always
"""

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'get']),
        topic_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        color=dict(type='str', required=False),
        api_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
        topic=None
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
        if module.params['topic_id']:
            url = f"{api_url}/topic/{module.params['topic_id']}.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['topic'] = resp.json()
        else:
            url = f"{api_url}/topics.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['topic'] = resp.json()
        module.exit_json(**result)
    elif module.params['state'] == 'present':
        if not module.params['topic_id']:
            module.fail_json(msg="topic_id required for update")
        url = f"{api_url}/topic/{module.params['topic_id']}.{suffix}"
        data = {k: v for k, v in module.params.items() if k in [
            'name', 'description', 'color'
        ] and v is not None}
        resp = requests.post(url, auth=auth, headers=headers, json=data)
        result['changed'] = True
        result['topic'] = resp.json()
        module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")

def main():
    run_module()

if __name__ == '__main__':
    main()
