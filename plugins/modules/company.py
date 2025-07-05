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
    slug:
        description:
            - The slug (code) of the company (required by CLI)
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
    slug: 'TEST'

# Update company
- name: Update company
  multiflexi_company:
    name: 'Renamed Company'
    slug: 'TEST'

# Delete company
- name: Delete company
  multiflexi_company:
    slug: 'TEST'
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
            "slug": "TEST"
        }
"""


def run_cli_command(args, module=None):
    # Use module._verbosity if available, else check ANSIBLE_VERBOSITY env var
    verbosity = 0
    if module and hasattr(module, '_verbosity'):
        verbosity = module._verbosity
    else:
        import os
        try:
            verbosity = int(os.environ.get('ANSIBLE_VERBOSITY', '0'))
        except Exception:
            verbosity = 0
    if verbosity >= 2 and module is not None:
        module.warn("[DEBUG] Running command: {}".format(' '.join(args)))
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"multiflexi-cli error: {e.stderr.strip()}")


def run_module():
    module_args = dict(
        id=dict(type='int', required=False),
        slug=dict(type='str', required=True),
        name=dict(type='str', required=False),
        customer=dict(type='int', required=False),
        enabled=dict(type='bool', required=False),
        settings=dict(type='str', required=False),
        logo=dict(type='str', required=False),
        ic=dict(type='str', required=False),
        DatCreate=dict(type='str', required=False),
        DatUpdate=dict(type='str', required=False),
        email=dict(type='str', required=False),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent', 'get'])
    )

    result = dict(
        changed=False,
        slug=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_base = ['multiflexi-cli', 'company']

    def get_existing_company():
        # Use the most specific identifier available: id > ic > name > slug
        if module.params.get('id'):
            args = cli_base + ['get', '--id', str(module.params['id']), '--verbose', '--format', 'json']
        elif module.params.get('ic'):
            args = cli_base + ['get', '--ic', module.params['ic'], '--verbose', '--format', 'json']
        elif module.params.get('name'):
            args = cli_base + ['get', '--name', module.params['name'], '--verbose', '--format', 'json']
        else:
            args = cli_base + ['get', '--slug', module.params['slug'], '--verbose', '--format', 'json']
        try:
            output = run_cli_command(args, module=module)
            company = json.loads(output)
            if isinstance(company, dict) and company.get("status") == "not found":
                return None, company.get("message")
            if isinstance(company, dict) and company.get('id'):
                return company, None
        except Exception as e:
            return None, str(e)
        return None, None

    try:
        if state == 'get':
            company, notfound_msg = get_existing_company()
            if not company:
                module.exit_json(changed=False, company=None, msg=notfound_msg or "Company not found")
            result['company'] = company
            module.exit_json(**result)
        elif state == 'present':
            existing, notfound_msg = get_existing_company()
            changed = False
            update_fields = {}
            for param in ['slug', 'name', 'customer', 'enabled', 'settings', 'logo', 'ic', 'DatCreate', 'DatUpdate', 'email']:
                desired = module.params.get(param)
                if desired is not None:
                    if not existing or str(existing.get(param)) != str(int(desired)) if isinstance(desired, bool) else str(desired):
                        update_fields[param] = desired
                        changed = True
            if not existing:
                # Create
                args = cli_base + ['create']
                for k, v in update_fields.items():
                    args += [f'--{k}', str(int(v)) if isinstance(v, bool) else str(v)]
                args += ['--verbose', '--format', 'json']
                if module.check_mode:
                    result['changed'] = True
                    module.exit_json(**result)
                run_cli_command(args, module=module)
                result['changed'] = True
            elif changed:
                # Update only if something changed
                args = cli_base + ['update', '--id', str(existing['id'])]
                for k, v in update_fields.items():
                    args += [f'--{k}', str(int(v)) if isinstance(v, bool) else str(v)]
                args += ['--verbose', '--format', 'json']
                if module.check_mode:
                    result['changed'] = True
                    module.exit_json(**result)
                run_cli_command(args, module=module)
                result['changed'] = True
            else:
                # No change needed
                result['changed'] = False
            # Always return the latest record
            latest, notfound_msg = get_existing_company()
            result['company'] = latest
            if not latest and notfound_msg:
                result['msg'] = notfound_msg
            module.exit_json(**result)
        elif state == 'absent':
            existing, notfound_msg = get_existing_company()
            if existing:
                args = cli_base + ['remove', '--id', str(existing['id']), '--verbose', '--format', 'json']
                if module.check_mode:
                    result['changed'] = True
                    module.exit_json(**result)
                run_cli_command(args, module=module)
                result['changed'] = True
                result['company'] = existing
            else:
                result['changed'] = False
                result['company'] = None
                if notfound_msg:
                    result['msg'] = notfound_msg
            module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))


def main():
   run_module()


if __name__ == '__main__':
   main()
