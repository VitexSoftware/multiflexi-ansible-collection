#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: eventrule
short_description: Manage event rules in MultiFlexi

description:
    - This module allows you to create, update, remove and list event rules in MultiFlexi.
    - Event rules map incoming webhook events (evidence + operation) to MultiFlexi RunTemplates.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the event rule.
        required: true
        type: str
        choices: ['present', 'absent', 'list']
    eventrule_id:
        description:
            - The ID of the event rule.
        required: false
        type: int
    eventsource_id:
        description:
            - The ID of the event source this rule belongs to.
        required: false
        type: int
    runtemplate_id:
        description:
            - The ID of the RunTemplate to trigger when the rule matches.
        required: false
        type: int
    evidence:
        description:
            - The evidence type to match (e.g. faktura-vydana, banka).
        required: false
        type: str
    operation:
        description:
            - The operation to match (create, update, delete).
        required: false
        type: str
        choices: ['create', 'update', 'delete']
    condition:
        description:
            - Optional additional condition expression.
        required: false
        type: str
    env_mapping:
        description:
            - JSON string mapping event data fields to environment variables.
        required: false
        type: str
    enabled:
        description:
            - Whether the event rule is enabled.
        required: false
        type: bool
        default: true
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: List all event rules
  vitexus.multiflexi.eventrule:
    state: list

- name: Get an event rule by ID
  vitexus.multiflexi.eventrule:
    state: present
    eventrule_id: 1

- name: Create a new event rule
  vitexus.multiflexi.eventrule:
    state: present
    eventsource_id: 1
    runtemplate_id: 5
    evidence: "faktura-vydana"
    operation: "create"
    env_mapping: '{"INVOICE_ID": "recordid"}'

- name: Update an event rule
  vitexus.multiflexi.eventrule:
    state: present
    eventrule_id: 1
    enabled: false

- name: Remove an event rule
  vitexus.multiflexi.eventrule:
    state: absent
    eventrule_id: 1
"""

RETURN = """
eventrule:
    description: The event rule object or list of event rules.
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
        state=dict(type='str', required=True, choices=['present', 'absent', 'list']),
        eventrule_id=dict(type='int', required=False),
        eventsource_id=dict(type='int', required=False),
        runtemplate_id=dict(type='int', required=False),
        evidence=dict(type='str', required=False),
        operation=dict(type='str', required=False, choices=['create', 'update', 'delete']),
        condition=dict(type='str', required=False),
        env_mapping=dict(type='str', required=False),
        enabled=dict(type='bool', required=False, default=True),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        eventrule=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'eventrule']

    try:
        if state == 'list':
            args = cli_base + ['list', '--format', 'json']
            output = run_cli_command(args)
            result['eventrule'] = json.loads(output)
            result['msg'] = "Retrieved event rule list"

        elif state == 'present':
            if module.params.get('eventrule_id'):
                # Get existing event rule
                args = cli_base + ['get', '--id', str(module.params['eventrule_id']), '--format', 'json']
                output = run_cli_command(args)
                result['eventrule'] = json.loads(output)
                result['msg'] = f"Retrieved event rule {module.params['eventrule_id']}"

                # Update if any fields provided
                update_args = cli_base + ['update', '--id', str(module.params['eventrule_id'])]
                has_updates = False
                for field in ['eventsource_id', 'runtemplate_id', 'evidence', 'operation',
                              'condition', 'env_mapping']:
                    if module.params.get(field) is not None:
                        update_args.extend([f'--{field}', str(module.params[field])])
                        has_updates = True
                if module.params.get('enabled') is not None:
                    update_args.extend(['--enabled', '1' if module.params['enabled'] else '0'])
                    has_updates = True

                if has_updates:
                    if module.check_mode:
                        result['msg'] = f"Would update event rule {module.params['eventrule_id']}"
                        result['changed'] = True
                    else:
                        update_args.extend(['--format', 'json'])
                        run_cli_command(update_args)
                        result['changed'] = True
                        result['msg'] = f"Updated event rule {module.params['eventrule_id']}"

                        # Get updated record
                        args = cli_base + ['get', '--id', str(module.params['eventrule_id']), '--format', 'json']
                        output = run_cli_command(args)
                        result['eventrule'] = json.loads(output)
            else:
                # Create new event rule
                if not module.params.get('eventsource_id'):
                    module.fail_json(msg="eventsource_id is required for creating an event rule")
                if not module.params.get('runtemplate_id'):
                    module.fail_json(msg="runtemplate_id is required for creating an event rule")
                if not module.params.get('evidence'):
                    module.fail_json(msg="evidence is required for creating an event rule")
                if not module.params.get('operation'):
                    module.fail_json(msg="operation is required for creating an event rule")

                if module.check_mode:
                    result['msg'] = "Would create event rule"
                    result['changed'] = True
                else:
                    create_args = cli_base + ['create',
                        '--eventsource_id', str(module.params['eventsource_id']),
                        '--runtemplate_id', str(module.params['runtemplate_id']),
                        '--evidence', module.params['evidence'],
                        '--operation', module.params['operation'],
                        '--enabled', '1' if module.params.get('enabled', True) else '0',
                        '--format', 'json',
                    ]
                    for field in ['condition', 'env_mapping']:
                        if module.params.get(field):
                            create_args.extend([f'--{field}', str(module.params[field])])

                    output = run_cli_command(create_args)
                    result['eventrule'] = json.loads(output)
                    result['changed'] = True
                    result['msg'] = "Event rule created"

        elif state == 'absent':
            if not module.params.get('eventrule_id'):
                module.fail_json(msg="eventrule_id is required for absent state")

            if module.check_mode:
                result['msg'] = f"Would remove event rule {module.params['eventrule_id']}"
                result['changed'] = True
            else:
                args = cli_base + ['remove', '--id', str(module.params['eventrule_id']), '--format', 'json']
                output = run_cli_command(args)
                result['eventrule'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Removed event rule {module.params['eventrule_id']}"

    except Exception as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
