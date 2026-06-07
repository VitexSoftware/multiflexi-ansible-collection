#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: user_company
short_description: Manage user-company assignments in MultiFlexi

description:
    - This module allows you to assign or unassign users to companies in MultiFlexi.

author:
    - Vitex (@Vitexus)

options:
    state:
        description:
            - The desired state of the assignment.
        required: true
        type: str
        choices: ['present', 'absent']
    company_id:
        description:
            - The ID of the company.
        required: true
        type: int
    user_id:
        description:
            - The ID of the user.
        required: false
        type: int
    login:
        description:
            - The login of the user (alternative to user_id).
        required: false
        type: str
    email:
        description:
            - The email of the user (alternative to user_id).
        required: false
        type: str
    role:
        description:
            - The role of the user in the company.
        required: false
        type: str
        default: 'viewer'
        choices: ['admin', 'manager', 'viewer']
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'
"""

EXAMPLES = """
- name: Assign user to company
  user_company:
    state: present
    company_id: 1
    login: "jdoe"
    role: "admin"

- name: Unassign user from company
  user_company:
    state: absent
    company_id: 1
    user_id: 3
"""

RETURN = """
assignment:
    description: Assignment information.
    type: dict
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
        state=dict(type='str', required=True, choices=['present', 'absent']),
        company_id=dict(type='int', required=True),
        user_id=dict(type='int', required=False),
        login=dict(type='str', required=False),
        email=dict(type='str', required=False),
        role=dict(type='str', required=False, default='viewer', choices=['admin', 'manager', 'viewer']),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        assignment=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'user-company']

    if not any([module.params.get('user_id'), module.params.get('login'), module.params.get('email')]):
        module.fail_json(msg="One of user_id, login, or email must be provided.")

    try:
        # Check for existing assignment?
        # The CLI doesn't seem to have a list command for user-company specifically,
        # but user:get often returns companies.

        # For simplicity and given CLI behavior, we'll try to determine if change is needed.
        # multiflexi-cli user-company:assign might be idempotent if it just sets the role.

        if state == 'present':
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)

            args = [cli_path, 'user-company:assign', '--company_id', str(module.params['company_id'])]
            if module.params.get('user_id'):
                args += ['--user_id', str(module.params['user_id'])]
            elif module.params.get('login'):
                args += ['--login', module.params['login']]
            elif module.params.get('email'):
                args += ['--email', module.params['email']]

            if module.params.get('role'):
                args += ['--role', module.params['role']]

            args += ['--format', 'json']
            output = run_cli_command(args)
            result['assignment'] = json.loads(output)
            result['changed'] = True

        elif state == 'absent':
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)

            args = [cli_path, 'user-company:unassign', '--company_id', str(module.params['company_id'])]
            if module.params.get('user_id'):
                args += ['--user_id', str(module.params['user_id'])]
            elif module.params.get('login'):
                args += ['--login', module.params['login']]
            elif module.params.get('email'):
                args += ['--email', module.params['email']]

            args += ['--format', 'json']
            output = run_cli_command(args)
            result['assignment'] = json.loads(output)
            result['changed'] = True

    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
