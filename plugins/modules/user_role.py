#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: user_role
short_description: Manage user RBAC roles in MultiFlexi

description:
    - This module allows you to set RBAC roles for a user in MultiFlexi.

author:
    - Vitex (@Vitexus)

options:
    user_id:
        description:
            - The ID of the user.
        required: false
        type: int
    login:
        description:
            - The login of the user.
        required: false
        type: str
    email:
        description:
            - The email of the user.
        required: false
        type: str
    roles:
        description:
            - Comma-separated list of RBAC role names.
        required: true
        type: list
        elements: str
    replace:
        description:
            - Whether to replace existing roles.
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
- name: Set user roles
  user_role:
    login: "jdoe"
    roles: ["admin", "viewer"]
    replace: true
"""

RETURN = """
roles:
    description: Updated user roles information.
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
        user_id=dict(type='int', required=False),
        login=dict(type='str', required=False),
        email=dict(type='str', required=False),
        roles=dict(type='list', elements='str', required=True),
        replace=dict(type='bool', required=False, default=True),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        roles=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    cli_path = module.params['multiflexi_cli_path']

    if not any([module.params.get('user_id'), module.params.get('login'), module.params.get('email')]):
        module.fail_json(msg="One of user_id, login, or email must be provided.")

    try:
        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        args = [cli_path, 'user-role:set']
        if module.params.get('user_id'):
            args += ['--user_id', str(module.params['user_id'])]
        elif module.params.get('login'):
            args += ['--login', module.params['login']]
        elif module.params.get('email'):
            args += ['--email', module.params['email']]

        args += ['--roles', ','.join(module.params['roles'])]
        args += ['--replace', 'true' if module.params['replace'] else 'false']
        args += ['--format', 'json']

        output = run_cli_command(args)
        result['roles'] = json.loads(output)
        result['changed'] = True

    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
