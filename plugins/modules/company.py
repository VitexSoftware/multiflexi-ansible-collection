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
    code:
        description:
            - The code of the company (required by CLI)
        required: true
        type: str
    name:
        description:
            - The name of the company
        required: false
        type: str
    customer:
        description:
            - The customer of the company
        required: false
        type: int
    server:
        description:
            - The server of the company
        required: false
        type: int
    enabled:
        description:
            - Enabled (true/false)
        required: false
        type: bool
    settings:
        description:
            - Settings
        required: false
        type: str
    logo:
        description:
            - Logo
        required: false
        type: str
    ic:
        description:
            - IC
        required: false
        type: str
    company:
        description:
            - Company Code
        required: false
        type: str
    rw:
        description:
            - Write permissions (true/false)
        required: false
        type: bool
    setup:
        description:
            - Setup (true/false)
        required: false
        type: bool
    webhook:
        description:
            - Webhook ready (true/false)
        required: false
        type: bool
    DatCreate:
        description:
            - Created date (date-time)
        required: false
        type: str
    DatUpdate:
        description:
            - Updated date (date-time)
        required: false
        type: str
    email:
        description:
            - Email
        required: false
        type: str
    state:
        description:
            - The state of the company
        required: false
        type: str
        choices: ['present', 'absent', 'get']
        default: 'present'
"""

EXAMPLES = """
# Create company
- name: Create company
  multiflexi_company:
    name: 'Test Company'
    code: 'TEST'

# Update company
- name: Update company
  multiflexi_company:
    name: 'Renamed Company'
    code: 'TEST'

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
            "code": "TEST"
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
        code=dict(type='str', required=True),
        name=dict(type='str', required=False),
        customer=dict(type='int', required=False),
        server=dict(type='int', required=False),
        enabled=dict(type='bool', required=False),
        settings=dict(type='str', required=False),
        logo=dict(type='str', required=False),
        ic=dict(type='str', required=False),
        company=dict(type='str', required=False),
        rw=dict(type='bool', required=False),
        setup=dict(type='bool', required=False),
        webhook=dict(type='bool', required=False),
        DatCreate=dict(type='str', required=False),
        DatUpdate=dict(type='str', required=False),
        email=dict(type='str', required=False),
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
            # Add all supported CLI options
            for param in ['code', 'name', 'customer', 'server', 'enabled', 'settings', 'logo', 'ic', 'company', 'rw', 'setup', 'webhook', 'DatCreate', 'DatUpdate', 'email']:
                value = module.params.get(param)
                if value is not None:
                    args += [f'--{param}', str(int(value)) if isinstance(value, bool) else str(value)]
            args += ['--format', 'json']
            output = run_cli_command(args)
            result['company'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'absent':
            args = cli_base + ['remove', '--code', module.params['code'], '--format', 'json']
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
