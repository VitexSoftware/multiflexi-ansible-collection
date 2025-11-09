#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: user_data_erasure
short_description: Manage GDPR user data erasure requests in MultiFlexi

description:
    - This module allows you to manage GDPR user data erasure requests in MultiFlexi.
    - Supports creating, listing, approving, rejecting, processing, auditing, and cleaning up erasure requests.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired action for user data erasure.
        required: true
        type: str
        choices: ['list', 'create', 'approve', 'reject', 'process', 'audit', 'cleanup']
    user_id:
        description:
            - The ID of the user for erasure operations.
        required: false
        type: int
    user_login:
        description:
            - The login of the user for erasure operations.
        required: false
        type: str
    request_id:
        description:
            - The ID of the erasure request.
        required: false
        type: int
    deletion_type:
        description:
            - Type of deletion for create operation.
        required: false
        type: str
        choices: ['soft', 'hard']
        default: 'soft'
    reason:
        description:
            - Reason for the erasure request.
        required: false
        type: str
    notes:
        description:
            - Additional notes for approve/reject operations.
        required: false
        type: str
    force:
        description:
            - Force the operation (for process action).
        required: false
        type: bool
        default: false
    export_audit:
        description:
            - File path to export audit trail (for audit action).
        required: false
        type: str
    status:
        description:
            - Filter by status for list operation.
        required: false
        type: str
        choices: ['pending', 'approved', 'rejected', 'processed']
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: List all pending deletion requests
  user_data_erasure:
    state: list
    status: pending

- name: Create a soft deletion request for user
  user_data_erasure:
    state: create
    user_id: 123
    deletion_type: soft
    reason: "User requested account deletion"

- name: Create deletion request by user login
  user_data_erasure:
    state: create
    user_login: "john.doe"
    deletion_type: soft
    reason: "GDPR compliance request"

- name: Approve a deletion request
  user_data_erasure:
    state: approve
    request_id: 456
    notes: "Approved by admin after verification"

- name: Reject a deletion request
  user_data_erasure:
    state: reject
    request_id: 456
    notes: "Insufficient documentation provided"

- name: Process an approved deletion request
  user_data_erasure:
    state: process
    request_id: 456

- name: Get audit trail for a deletion request
  user_data_erasure:
    state: audit
    request_id: 456
    export_audit: "/tmp/audit_trail.csv"

- name: Cleanup completed requests
  user_data_erasure:
    state: cleanup
"""

RETURN = """
erasure_request:
    description: The erasure request object or list of requests.
    type: dict or list
    returned: always
msg:
    description: A message describing the action taken.
    type: str
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
        state=dict(type='str', required=True, choices=['list', 'create', 'approve', 'reject', 'process', 'audit', 'cleanup']),
        user_id=dict(type='int', required=False),
        user_login=dict(type='str', required=False),
        request_id=dict(type='int', required=False),
        deletion_type=dict(type='str', required=False, choices=['soft', 'hard'], default='soft'),
        reason=dict(type='str', required=False),
        notes=dict(type='str', required=False),
        force=dict(type='bool', required=False, default=False),
        export_audit=dict(type='str', required=False),
        status=dict(type='str', required=False, choices=['pending', 'approved', 'rejected', 'processed']),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        erasure_request=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'user:data-erasure']

    try:
        if state == 'list':
            args = cli_base + ['list', '--format', 'json']
            if module.params.get('status'):
                args.extend(['--status', module.params['status']])
            output = run_cli_command(args)
            result['erasure_request'] = json.loads(output)
            result['msg'] = "Retrieved erasure request list"
            
        elif state == 'create':
            if not (module.params.get('user_id') or module.params.get('user_login')):
                module.fail_json(msg="Either user_id or user_login is required for create operation")
                
            if module.check_mode:
                result['msg'] = f"Would create erasure request for user"
                result['changed'] = True
            else:
                args = cli_base + ['create', '--deletion-type', module.params['deletion_type'], '--format', 'json']
                
                if module.params.get('user_id'):
                    args.extend(['--user-id', str(module.params['user_id'])])
                elif module.params.get('user_login'):
                    args.extend(['--user-login', module.params['user_login']])
                    
                if module.params.get('reason'):
                    args.extend(['--reason', module.params['reason']])
                    
                output = run_cli_command(args)
                result['erasure_request'] = json.loads(output)
                result['changed'] = True
                result['msg'] = "Created erasure request"
                
        elif state == 'approve':
            if not module.params.get('request_id'):
                module.fail_json(msg="request_id is required for approve operation")
                
            if module.check_mode:
                result['msg'] = f"Would approve erasure request {module.params['request_id']}"
                result['changed'] = True
            else:
                args = cli_base + ['approve', '--request-id', str(module.params['request_id']), '--format', 'json']
                if module.params.get('notes'):
                    args.extend(['--notes', module.params['notes']])
                    
                output = run_cli_command(args)
                result['erasure_request'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Approved erasure request {module.params['request_id']}"
                
        elif state == 'reject':
            if not module.params.get('request_id'):
                module.fail_json(msg="request_id is required for reject operation")
                
            if module.check_mode:
                result['msg'] = f"Would reject erasure request {module.params['request_id']}"
                result['changed'] = True
            else:
                args = cli_base + ['reject', '--request-id', str(module.params['request_id']), '--format', 'json']
                if module.params.get('notes'):
                    args.extend(['--notes', module.params['notes']])
                    
                output = run_cli_command(args)
                result['erasure_request'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Rejected erasure request {module.params['request_id']}"
                
        elif state == 'process':
            if not module.params.get('request_id'):
                module.fail_json(msg="request_id is required for process operation")
                
            if module.check_mode:
                result['msg'] = f"Would process erasure request {module.params['request_id']}"
                result['changed'] = True
            else:
                args = cli_base + ['process', '--request-id', str(module.params['request_id']), '--format', 'json']
                if module.params.get('force'):
                    args.append('--force')
                    
                output = run_cli_command(args)
                result['erasure_request'] = json.loads(output)
                result['changed'] = True
                result['msg'] = f"Processed erasure request {module.params['request_id']}"
                
        elif state == 'audit':
            if not module.params.get('request_id'):
                module.fail_json(msg="request_id is required for audit operation")
                
            args = cli_base + ['audit', '--request-id', str(module.params['request_id']), '--format', 'json']
            if module.params.get('export_audit'):
                args.extend(['--export-audit', module.params['export_audit']])
                result['changed'] = True  # File was exported
                
            output = run_cli_command(args)
            result['erasure_request'] = json.loads(output)
            result['msg'] = f"Retrieved audit trail for request {module.params['request_id']}"
            
        elif state == 'cleanup':
            if module.check_mode:
                result['msg'] = "Would cleanup completed erasure requests"
                result['changed'] = True
            else:
                args = cli_base + ['cleanup', '--format', 'json']
                output = run_cli_command(args)
                result['erasure_request'] = json.loads(output)
                result['changed'] = True
                result['msg'] = "Cleaned up completed erasure requests"
            
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()