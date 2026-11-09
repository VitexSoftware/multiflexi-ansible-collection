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
            - The operation to match. Known values are C(any), C(create), C(update),
              C(delete) and the invoice metastates emitted by abraflexi-webhook-acceptor
              on top of a raw C(update) notification - C(settled) (invoice fully paid),
              C(remind1), C(remind2), C(remind3), C(penalised), C(storno), C(inventory).
            - Any other adapter-specific operation string is accepted as-is
              (same as multiflexi-cli and the REST API), so rules keep working
              when a new metastate is introduced.
        required: false
        type: str
    priority:
        description:
            - Priority (higher = matched first).
        required: false
        type: int
        default: 0
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

- name: React to a fully paid invoice (metastate emitted by abraflexi-webhook-acceptor)
  vitexus.multiflexi.eventrule:
    state: present
    eventsource_id: 1
    runtemplate_id: 55
    evidence: "faktura-vydana"
    operation: "settled"
    env_mapping: '{\"ABRAFLEXI_CUSTOMER\": \"firma\", \"INVOICE_ID\": \"recordid\"}'

- name: React to a changed contract and mail it to the customer
  vitexus.multiflexi.eventrule:
    state: present
    eventsource_id: 1
    runtemplate_id: 60
    evidence: "smlouva"
    operation: "any"
    env_mapping: '{\"EVENT_RECORD_ID\": \"recordid\"}'

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
        operation=dict(type='str', required=False),
        priority=dict(type='int', required=False, default=0),
        env_mapping=dict(type='str', required=False),
        enabled=dict(type='bool', required=False, default=True),
        limit=dict(type='int', required=False),
        order=dict(type='str', required=False),
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
    cli_base = [cli_path]

    try:
        if state == 'list':
            args = cli_base + ['event-rule:list', '--format', 'json']
            if module.params.get('limit'):
                args.extend(['--limit', str(module.params['limit'])])
            if module.params.get('order'):
                args.extend(['--order', module.params['order']])
            output = run_cli_command(args)
            result['eventrule'] = json.loads(output)
            result['msg'] = "Retrieved event rule list"

        elif state == 'present':
            # Idempotence: without an explicit id, look the rule up by its
            # identity (event source + run template + evidence + operation) so
            # re-running a playbook updates it instead of creating a duplicate.
            if not module.params.get('eventrule_id') and all(
                module.params.get(k) not in (None, '')
                for k in ('eventsource_id', 'runtemplate_id', 'evidence', 'operation')
            ):
                listed = json.loads(run_cli_command(cli_base + ['event-rule:list', '--format', 'json']))
                if isinstance(listed, list):
                    for item in listed:
                        if not isinstance(item, dict) or item.get('id') is None:
                            continue
                        src = item.get('event_source_id', item.get('eventsource_id'))
                        if (str(src) == str(module.params['eventsource_id'])
                                and str(item.get('runtemplate_id')) == str(module.params['runtemplate_id'])
                                and str(item.get('evidence')) == str(module.params['evidence'])
                                and str(item.get('operation')) == str(module.params['operation'])):
                            module.params['eventrule_id'] = int(item['id'])
                            break

            if module.params.get('eventrule_id'):
                # Get existing event rule
                args = cli_base + ['event-rule:get', '--id', str(module.params['eventrule_id']), '--format', 'json']
                output = run_cli_command(args)
                result['eventrule'] = json.loads(output)
                result['msg'] = f"Retrieved event rule {module.params['eventrule_id']}"

                # Update if any fields provided
                # Module param name -> CLI option name (eventsource_id maps to --event_source_id)
                update_fields = {
                    'eventsource_id': 'event_source_id',
                    'runtemplate_id': 'runtemplate_id',
                    'evidence': 'evidence',
                    'operation': 'operation',
                    'env_mapping': 'env_mapping',
                    'priority': 'priority',
                }
                update_args = cli_base + ['event-rule:update', '--id', str(module.params['eventrule_id'])]
                existing = result['eventrule'] if isinstance(result.get('eventrule'), dict) else {}

                def _same(wanted, current):
                    # env_mapping may be stored as a JSON string or a decoded dict
                    if wanted is None or current is None:
                        return False
                    if isinstance(current, (dict, list)) or str(wanted).lstrip().startswith(('{', '[')):
                        try:
                            w = json.loads(wanted) if isinstance(wanted, str) else wanted
                            c = json.loads(current) if isinstance(current, str) else current
                            return w == c
                        except ValueError:
                            pass
                    return str(wanted) == str(current)

                has_updates = False
                for field, cli_name in update_fields.items():
                    if module.params.get(field) is None:
                        continue
                    current = existing.get(cli_name, existing.get(field))
                    if not _same(module.params[field], current):
                        update_args.extend([f'--{cli_name}', str(module.params[field])])
                        has_updates = True
                if module.params.get('enabled') is not None:
                    if str(int(bool(module.params['enabled']))) != str(existing.get('enabled')):
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
                        args = cli_base + ['event-rule:get', '--id', str(module.params['eventrule_id']), '--format', 'json']
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
                    create_args = cli_base + ['event-rule:create',
                        '--event_source_id', str(module.params['eventsource_id']),
                        '--runtemplate_id', str(module.params['runtemplate_id']),
                        '--evidence', module.params['evidence'],
                        '--operation', module.params['operation'],
                        '--enabled', '1' if module.params.get('enabled', True) else '0',
                        '--format', 'json',
                    ]
                    for field in ['env_mapping', 'priority']:
                        if module.params.get(field) is not None:
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
                args = cli_base + ['event-rule:remove', '--id', str(module.params['eventrule_id']), '--format', 'json']
                output = run_cli_command(args)
                result['eventrule'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Removed event rule {module.params['eventrule_id']}"

    except Exception as e:
        result['msg'] = str(e)
        module.fail_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
