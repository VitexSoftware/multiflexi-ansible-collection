#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: topic
short_description: Manage topics in Multiflexi

description:
    - This module allows you to get and update topics in Multiflexi via CLI with idempotency logic.

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
    multiflexi_cli:
        description:
            - Path to multiflexi-cli binary (default: multiflexi-cli in PATH).
        required: false
        type: str
        default: multiflexi-cli
"""

EXAMPLES = """
- name: Get a topic by ID
  topic:
    state: get
    topic_id: 1

- name: List all topics
  topic:
    state: get

- name: Update a topic
  topic:
    state: present
    topic_id: 1
    name: "Important"
    color: "#ff0000"
"""

RETURN = """
topic:
    description: The topic object or list of topics.
    type: dict or list
    returned: always
"""

def run_cli(module, args):
    cli = module.params.get('multiflexi_cli', 'multiflexi-cli')
    cmd = [cli] + args + ['--verbose', '--format', 'json']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        try:
            err = json.loads(e.stdout or e.stderr)
        except Exception:
            err = e.stdout or e.stderr
        module.fail_json(msg=f"CLI error: {err}", rc=e.returncode)
    except Exception as e:
        module.fail_json(msg=f"Failed to run CLI: {e}")

def find_existing_topic(module):
    # Priority: topic_id > name
    if module.params.get('topic_id'):
        res = run_cli(module, ['topic', 'get', '--id', str(module.params['topic_id'])])
        if isinstance(res, dict) and res.get('id'):
            return res
    elif module.params.get('name'):
        topics = run_cli(module, ['topic', 'list'])
        for topic in topics if isinstance(topics, list) else []:
            if topic.get('name') == module.params['name']:
                return topic
    return None

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'get']),
        topic_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        color=dict(type='str', required=False),
        multiflexi_cli=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        topic=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']

    if state == 'get':
        topic = find_existing_topic(module)
        if topic:
            result['topic'] = topic
        else:
            topics = run_cli(module, ['topic', 'list'])
            result['topic'] = topics
        module.exit_json(**result)

    elif state == 'present':
        topic = find_existing_topic(module)
        if not topic:
            module.fail_json(msg="Topic not found. Creation is not supported via CLI.")
        # Prepare update args (only supported fields)
        update_args = ['topic', 'update', '--id', str(topic['id'])]
        for field in ['name', 'description', 'color']:
            val = module.params.get(field)
            if val is not None:
                update_args += [f'--{field}', str(val)]
        if module.check_mode:
            result['changed'] = True
            result['topic'] = topic
            module.exit_json(**result)
        run_cli(module, update_args)
        latest = run_cli(module, ['topic', 'get', '--id', str(topic['id'])])
        result['changed'] = True
        result['topic'] = latest
        module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")

def main():
    run_module()

if __name__ == '__main__':
    main()
