#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>


from __future__ import absolute_import, division, print_function
import subprocess
import json
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type


DOCUMENTATION = """
---
module: company

short_description: Create, update or delete company in Multiflexi

description:
    - This module allows you to create, update or delete company in Multiflexi

author:
    - Vitex (@Vitexus)

requirements:
    - "python >= 3.9"

version_added: 2.1.0

options:
    name:
        description:
            - The name of the company
        required: true
        type: str
    ico:
        description:
            - The ICO of the company
        required: true
        type: str
    code:
        description:
            - The CODE of the company
        required: true
        type: str
    email:
        description:
            - The email of the company
        required: false
        type: str
    state:
        description:
            - The state of the company
        required: false
        type: str
        choices: ['present', 'absent']
        default: 'present'
    enabled:
        description:
            - The enabled state of the company
        required: false
        type: bool
        default: true
    settings:
        description:
            - The settings of the company
        required: false
        type: str
    logo:
        description:
            - The logo of the company
        required: false
        type: str
    server:
        description:
            - The server of the company
        required: false
        type: int
    rw:
        description:
            - The read/write state of the company
        required: false
        type: bool
    setup:
        description:
            - The setup state of the company
        required: false
        type: bool
    webhook:
        description:
            - The webhook state of the company
        required: false
        type: bool
    customer:
        description:
            - The customer of the company
        required: false
        type: int
"""

EXAMPLES = """
# Create company
- name: Create company
  multiflexi_company:
    name: 'Test Company'
    ico: '12345678'
    code: 'TEST'
    email: 'your@mail.com'

# Update company
- name: Update company
  multiflexi_company:
    name: 'Renamed Company'
    code: 'TEST'
    email: 'fixed@mail.com'

# Delete company
- name: Delete company
  multiflexi_company:
    code: 'TEST'
    state: 'absent'
"""

RETURN = """
company:
    description: The company
    type: dict
    returned: always
    sample:
        {
            "id": 1,
            "name": "Test Company",
            "ico": "12345678",
            "code": "TEST",
            "email": "your@email.com"
        }
"""


def run_cli_command(args):
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"multiflexi-cli error: {e.stderr.strip()}")


def run_module():
    module_args = dict(
        id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        ico=dict(type='str', required=False),
        code=dict(type='str', required=True),
        email=dict(type='str', required=False),
        enabled=dict(type='bool', required=False),
        settings=dict(type='str', required=False),
        logo=dict(type='str', required=False),
        server=dict(type='int', required=False),
        rw=dict(type='bool', required=False),
        setup=dict(type='bool', required=False),
        webhook=dict(type='bool', required=False),
        customer=dict(type='int', required=False),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent', 'get'])
    )

    result = dict(
        changed=False,
        company=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_base = ['multiflexi-cli', 'company']

    try:
        if state == 'get':
            args = cli_base + ['get', '--code', module.params['code'], '--format', 'json']
            output = run_cli_command(args)
            result['company'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'present':
            # If id is provided, update; else, create
            if module.params.get('id'):
                args = cli_base + ['update', '--id', str(module.params['id'])]
                result['changed'] = True
            else:
                args = cli_base + ['create']
                result['changed'] = True
            # Add optional parameters
            for param in ['name', 'ico', 'code', 'email', 'enabled', 'settings', 'logo', 'server', 'rw', 'setup', 'webhook', 'customer']:
                value = module.params.get(param)
                if value is not None:
                    args += [f'--{param}', str(int(value)) if isinstance(value, bool) else str(value)]
            args += ['--format', 'json']
            output = run_cli_command(args)
            result['company'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'absent':
            args = cli_base + ['delete', '--code', module.params['code'], '--format', 'json']
            output = run_cli_command(args)
            result['changed'] = True
            result['company'] = json.loads(output)
            module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))


def main():
   run_module()


if __name__ == '__main__':
   main()
