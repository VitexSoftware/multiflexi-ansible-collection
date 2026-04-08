#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: eventsource
short_description: Manage event sources in MultiFlexi

description:
    - This module allows you to create, update, remove, list and test event sources in MultiFlexi.
    - Event sources represent external webhook adapter database connections that the event processor polls for changes.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the event source.
        required: true
        type: str
        choices: ['present', 'absent', 'list', 'test']
    eventsource_id:
        description:
            - The ID of the event source.
        required: false
        type: int
    name:
        description:
            - Name of the event source.
        required: false
        type: str
    adapter_type:
        description:
            - Type of webhook adapter (e.g. abraflexi-webhook-acceptor).
        required: false
        type: str
    db_connection:
        description:
            - Database driver (mysql, pgsql, sqlite).
        required: false
        type: str
        default: 'mysql'
    db_host:
        description:
            - Database host.
        required: false
        type: str
        default: 'localhost'
    db_port:
        description:
            - Database port.
        required: false
        type: str
        default: '3306'
    db_database:
        description:
            - Database name.
        required: false
        type: str
    db_username:
        description:
            - Database username.
        required: false
        type: str
    db_password:
        description:
            - Database password.
        required: false
        type: str
        no_log: true
    poll_interval:
        description:
            - Poll interval in seconds.
        required: false
        type: int
        default: 60
    enabled:
        description:
            - Whether the event source is enabled.
        required: false
        type: bool
        default: true
    limit:
        description:
            - Limit number of results for list action.
        required: false
        type: int
    order:
        description:
            - Sort order for list action.
        required: false
        type: str
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: List all event sources
  vitexus.multiflexi.eventsource:
    state: list

- name: Get an event source by ID
  vitexus.multiflexi.eventsource:
    state: present
    eventsource_id: 1

- name: Create a new event source
  vitexus.multiflexi.eventsource:
    state: present
    name: "AbraFlexi Webhooks"
    adapter_type: "abraflexi-webhook-acceptor"
    db_connection: mysql
    db_host: localhost
    db_database: webhooks
    db_username: webhook_user
    db_password: secret

- name: Update an event source
  vitexus.multiflexi.eventsource:
    state: present
    eventsource_id: 1
    name: "Updated Name"
    poll_interval: 120

- name: Test event source connection
  vitexus.multiflexi.eventsource:
    state: test
    eventsource_id: 1

- name: Remove an event source
  vitexus.multiflexi.eventsource:
    state: absent
    eventsource_id: 1
"""

RETURN = """
eventsource:
    description: The event source object or list of event sources.
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
        state=dict(type='str', required=True, choices=['present', 'absent', 'list', 'test']),
        eventsource_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        adapter_type=dict(type='str', required=False),
        db_connection=dict(type='str', required=False, default='mysql'),
        db_host=dict(type='str', required=False, default='localhost'),
        db_port=dict(type='str', required=False, default='3306'),
        db_database=dict(type='str', required=False),
        db_username=dict(type='str', required=False),
        db_password=dict(type='str', required=False, no_log=True),
        poll_interval=dict(type='int', required=False, default=60),
        enabled=dict(type='bool', required=False, default=True),
        limit=dict(type='int', required=False),
        order=dict(type='str', required=False),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        eventsource=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'eventsource']

    try:
        if state == 'list':
            args = cli_base + ['list', '--format', 'json']
            if module.params.get('limit'):
                args.extend(['--limit', str(module.params['limit'])])
            if module.params.get('order'):
                args.extend(['--order', module.params['order']])
            output = run_cli_command(args)
            result['eventsource'] = json.loads(output)
            result['msg'] = "Retrieved event source list"

        elif state == 'present':
            if module.params.get('eventsource_id'):
                # Get existing event source
                args = cli_base + ['get', '--id', str(module.params['eventsource_id']), '--format', 'json']
                output = run_cli_command(args)
                result['eventsource'] = json.loads(output)
                result['msg'] = f"Retrieved event source {module.params['eventsource_id']}"

                # Update if any fields provided
                update_args = cli_base + ['update', '--id', str(module.params['eventsource_id'])]
                has_updates = False
                for field in ['name', 'adapter_type', 'db_connection', 'db_host', 'db_port',
                              'db_database', 'db_username', 'db_password']:
                    if module.params.get(field):
                        update_args.extend([f'--{field}', str(module.params[field])])
                        has_updates = True
                if module.params.get('poll_interval') != 60:
                    update_args.extend(['--poll_interval', str(module.params['poll_interval'])])
                    has_updates = True

                if has_updates:
                    if module.check_mode:
                        result['msg'] = f"Would update event source {module.params['eventsource_id']}"
                        result['changed'] = True
                    else:
                        update_args.extend(['--format', 'json'])
                        run_cli_command(update_args)
                        result['changed'] = True
                        result['msg'] = f"Updated event source {module.params['eventsource_id']}"

                        # Get updated record
                        args = cli_base + ['get', '--id', str(module.params['eventsource_id']), '--format', 'json']
                        output = run_cli_command(args)
                        result['eventsource'] = json.loads(output)
            else:
                # Create new event source
                if not module.params.get('name'):
                    module.fail_json(msg="name parameter is required for creating an event source")

                if module.check_mode:
                    result['msg'] = f"Would create event source '{module.params['name']}'"
                    result['changed'] = True
                else:
                    create_args = cli_base + ['create',
                        '--name', module.params['name'],
                        '--db_connection', module.params.get('db_connection', 'mysql'),
                        '--db_host', module.params.get('db_host', 'localhost'),
                        '--db_port', module.params.get('db_port', '3306'),
                        '--poll_interval', str(module.params.get('poll_interval', 60)),
                        '--enabled', '1' if module.params.get('enabled', True) else '0',
                        '--format', 'json',
                    ]
                    for field in ['adapter_type', 'db_database', 'db_username', 'db_password']:
                        if module.params.get(field):
                            create_args.extend([f'--{field}', str(module.params[field])])

                    output = run_cli_command(create_args)
                    result['eventsource'] = json.loads(output)
                    result['changed'] = True
                    result['msg'] = "Event source created"

        elif state == 'absent':
            if not module.params.get('eventsource_id'):
                module.fail_json(msg="eventsource_id is required for absent state")

            if module.check_mode:
                result['msg'] = f"Would remove event source {module.params['eventsource_id']}"
                result['changed'] = True
            else:
                args = cli_base + ['remove', '--id', str(module.params['eventsource_id']), '--format', 'json']
                output = run_cli_command(args)
                result['eventsource'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Removed event source {module.params['eventsource_id']}"

        elif state == 'test':
            if not module.params.get('eventsource_id'):
                module.fail_json(msg="eventsource_id is required for test state")

            args = cli_base + ['test', '--id', str(module.params['eventsource_id']), '--format', 'json']
            output = run_cli_command(args)
            result['eventsource'] = json.loads(output)
            result['msg'] = "Connection test completed"

    except Exception as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
