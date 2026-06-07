#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: user_erasure
short_description: Manage GDPR user data erasure requests in MultiFlexi

description:
    - This module allows you to manage GDPR user data erasure requests in MultiFlexi.
    - Supports creating, listing, approving, rejecting, and processing erasure requests.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired action for the erasure request.
        required: true
        type: str
        choices: ['present', 'list', 'approve', 'reject', 'process', 'audit', 'cleanup']
    request_id:
        description:
            - The ID of the erasure request.
        required: false
        type: int
    user_id:
        description:
            - The ID of the user.
        required: false
        type: int
    user_login:
        description:
            - The login of the user.
        required: false
        type: str
    deletion_type:
        description:
            - Type of deletion.
        required: false
        type: str
        choices: ['soft', 'hard', 'anonymize']
        default: 'soft'
    reason:
        description:
            - Reason for the deletion request.
        required: false
        type: str
    notes:
        description:
            - Notes for approval/rejection.
        required: false
        type: str
    status:
        description:
            - Filter for list action.
        required: false
        type: str
        choices: ['pending', 'approved', 'rejected', 'completed']
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: Create erasure request
  user_erasure:
    state: present
    user_login: "jdoe"
    deletion_type: "soft"
    reason: "User requested data deletion"

- name: List erasure requests
  user_erasure:
    state: list
    status: "pending"

- name: Approve erasure request
  user_erasure:
    state: approve
    request_id: 1
    notes: "Verified user identity"
"""

RETURN = """
erasure:
    description: Erasure request information.
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
        state=dict(type='str', required=True, choices=['present', 'list', 'approve', 'reject', 'process', 'audit', 'cleanup']),
        request_id=dict(type='int', required=False),
        user_id=dict(type='int', required=False),
        user_login=dict(type='str', required=False),
        deletion_type=dict(type='str', required=False, default='soft', choices=['soft', 'hard', 'anonymize']),
        reason=dict(type='str', required=False),
        notes=dict(type='str', required=False),
        status=dict(type='str', required=False, choices=['pending', 'approved', 'rejected', 'completed']),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        erasure=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']

    try:
        if state == 'list':
            args = [cli_path, 'user-erasure:list', '--format', 'json']
            if module.params.get('status'):
                args += ['--status', module.params['status']]
            output = run_cli_command(args)
            result['erasure'] = json.loads(output)

        elif state == 'present':
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            args = [cli_path, 'user-erasure:create']
            if module.params.get('user_id'):
                args += ['--user-id', str(module.params['user_id'])]
            elif module.params.get('user_login'):
                args += ['--user-login', module.params['user_login']]
            else:
                module.fail_json(msg="user_id or user_login is required for present state")

            args += ['--deletion-type', module.params['deletion_type']]
            if module.params.get('reason'):
                args += ['--reason', module.params['reason']]
            args += ['--force'] # To avoid interaction

            output = run_cli_command(args)
            # creation may not return JSON by default or different format
            result['changed'] = True

        elif state == 'approve':
            if not module.params.get('request_id'):
                module.fail_json(msg="request_id is required for approve state")
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            args = [cli_path, 'user-erasure:approve', '--request-id', str(module.params['request_id']), '--force']
            if module.params.get('notes'):
                args += ['--notes', module.params['notes']]
            run_cli_command(args)
            result['changed'] = True

        elif state == 'reject':
            if not module.params.get('request_id'):
                module.fail_json(msg="request_id is required for reject state")
            if not module.params.get('reason'):
                module.fail_json(msg="reason is required for reject state")
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            args = [cli_path, 'user-erasure:reject', '--request-id', str(module.params['request_id']), '--reason', module.params['reason'], '--force']
            run_cli_command(args)
            result['changed'] = True

        elif state == 'process':
            if not module.params.get('request_id'):
                module.fail_json(msg="request_id is required for process state")
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            args = [cli_path, 'user-erasure:process', '--request-id', str(module.params['request_id'])]
            run_cli_command(args)
            result['changed'] = True

        elif state == 'audit':
            if not module.params.get('request_id'):
                module.fail_json(msg="request_id is required for audit state")
            args = [cli_path, 'user-erasure:audit', '--request-id', str(module.params['request_id'])]
            output = run_cli_command(args)
            result['erasure'] = output # Audit is likely text

        elif state == 'cleanup':
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            args = [cli_path, 'user-erasure:cleanup']
            run_cli_command(args)
            result['changed'] = True

    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
