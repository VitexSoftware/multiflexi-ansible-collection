#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>

DOCUMENTATION = """
---
module: companyapp

short_description: Manage company-application relations in Multiflexi

description:
    - This module allows you to create, update, get, and delete company-application relations in Multiflexi using the multiflexi-cli.

author:
    - Vitex (@Vitexus)

version_added: "2.1.0"

options:
    state:
        description:
            - The state of the company-application relation.
        required: false
        type: str
        choices: ['present', 'absent', 'get']
        default: 'present'
    relation_id:
        description:
            - The ID of the company-application relation.
        required: false
        type: int
    company_id:
        description:
            - The ID of the company.
        required: false
        type: int
    app_id:
        description:
            - The ID of the application.
        required: false
        type: int
    app_uuid:
        description:
            - The UUID of the application.
        required: false
        type: str
"""

EXAMPLES = """
    - name: Assign application to company
      vitexus.multiflexi.companyapp:
        state: present
        company_id: 1
        app_uuid: "262dabf1-d7b1-42c8-91a1-fe991631547c"

    - name: Remove application from company
      vitexus.multiflexi.companyapp:
        state: absent
        relation_id: 123

    - name: Get company-application relation details
      vitexus.multiflexi.companyapp:
        state: get
        relation_id: 123
"""

RETURN = """
    message:
        description: The output message that the module generates.
        type: str
        returned: always
    changed:
        description: Whether the relation was changed.
        type: bool
        returned: always
    companyapp:
        description: The company-application relation data.
        type: dict
        returned: when state is present or get
"""


from ansible.module_utils.basic import AnsibleModule
import subprocess
import json


def run_cli_command(args, module=None, allow_not_found=False):
    if module and module._verbosity >= 2:
        module.warn(f"Running CLI command: {' '.join(args)}")
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        if module and module._verbosity >= 2:
            module.warn(f"CLI stdout: {result.stdout.strip()}")
            if result.stderr.strip():
                module.warn(f"CLI stderr: {result.stderr.strip()}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if hasattr(e, 'stdout') and e.stdout else ''
        stderr = e.stderr.strip() if hasattr(e, 'stderr') and e.stderr else ''
        if module and module._verbosity >= 2:
            module.warn(f"CLI error: {stderr}")
            if stdout:
                module.warn(f"CLI stdout (on error): {stdout}")

        # Handle "already exists" case for create operations
        if allow_not_found or 'already exists' in stderr.lower() or 'already exists' in stdout.lower():
            return stdout or stderr

        try:
            if stdout:
                data = json.loads(stdout)
                if isinstance(data, dict) and data.get('message'):
                    raise Exception(f"multiflexi-cli error: {data.get('message')}")
        except Exception:
            pass
        raise Exception(f"multiflexi-cli error: {stderr or stdout or str(e)}")


def run_module():
    module_args = dict(
        state=dict(type='str', required=False, default='present', choices=['present', 'absent', 'get']),
        relation_id=dict(type='int', required=False),
        company_id=dict(type='int', required=False),
        app_id=dict(type='int', required=False),
        app_uuid=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        companyapp=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params.get('state')
    cli_base = ['multiflexi-cli']

    try:
        # Helper to find an existing relation
        def find_existing_relation():
            relation_id = module.params.get('relation_id')
            company_id = module.params.get('company_id')
            app_id = module.params.get('app_id')
            app_uuid = module.params.get('app_uuid')

            list_args = cli_base + ['company-app:list', '--format', 'json']
            if company_id:
                list_args += ['--company_id', str(company_id)]
            if app_id:
                list_args += ['--app_id', str(app_id)]
            elif app_uuid:
                list_args += ['--app_uuid', app_uuid]

            try:
                output = run_cli_command(list_args, module=module, allow_not_found=True)
                relations = json.loads(output)
                if isinstance(relations, list):
                    if relation_id:
                        for r in relations:
                            if r.get('id') == relation_id:
                                return r
                    elif len(relations) > 0:
                        return relations[0]
            except Exception:
                pass
            return None

        if state == 'get':
            relation = find_existing_relation()
            if relation:
                result['companyapp'] = relation
            else:
                if module.params.get('relation_id') or (module.params.get('company_id') and (module.params.get('app_id') or module.params.get('app_uuid'))):
                    result['companyapp'] = None
                    result['message'] = 'Relation not found'
                else:
                    # List all
                    list_args = cli_base + ['company-app:list', '--format', 'json', '--verbose']
                    output = run_cli_command(list_args, module=module, allow_not_found=True)
                    try:
                        result['companyapp'] = json.loads(output)
                    except json.JSONDecodeError:
                        result['companyapp'] = None
                        result['message'] = 'No relations found or invalid response'
            module.exit_json(**result)

        elif state == 'present':
            # Check if relation already exists
            existing_relation = find_existing_relation()

            if existing_relation:
                result['changed'] = False
                result['companyapp'] = existing_relation
                result['message'] = 'Company-application relation already exists'
            else:
                # Create new relation using company-app:assign
                company_id = module.params.get('company_id')
                app_id = module.params.get('app_id')
                app_uuid = module.params.get('app_uuid')

                if not company_id:
                    module.fail_json(msg='company_id is required for creating company-application relations')
                if not app_id and not app_uuid:
                    module.fail_json(msg='Either app_id or app_uuid is required for creating company-application relations')

                create_args = cli_base + ['company-app:assign', '--company_id', str(company_id)]
                if app_id:
                    create_args += ['--app_id', str(app_id)]
                elif app_uuid:
                    create_args += ['--app_uuid', app_uuid]

                if module.check_mode:
                    result['changed'] = True
                    result['companyapp'] = None
                    module.exit_json(**result)

                create_args += ['--format', 'json', '--verbose']
                run_cli_command(create_args, module=module)
                result['changed'] = True

                # Fetch the newly created assignment
                new_relation = find_existing_relation()
                result['companyapp'] = new_relation
            module.exit_json(**result)

        elif state == 'absent':
            existing_relation = find_existing_relation()

            if existing_relation:
                cid = module.params.get('company_id') or existing_relation.get('company_id')
                aid = module.params.get('app_id') or existing_relation.get('app_id')
                auuid = module.params.get('app_uuid') or existing_relation.get('app_uuid')

                if not cid:
                    module.fail_json(msg='company_id is required to remove company-application relation')
                if not aid and not auuid:
                    module.fail_json(msg='Either app_id or app_uuid is required to remove company-application relation')

                if module.check_mode:
                    result['changed'] = True
                    result['companyapp'] = existing_relation
                    module.exit_json(**result)

                delete_args = cli_base + ['company-app:unassign', '--company_id', str(cid)]
                if aid:
                    delete_args += ['--app_id', str(aid)]
                elif auuid:
                    delete_args += ['--app_uuid', auuid]
                delete_args += ['--format', 'json', '--verbose']

                run_cli_command(delete_args, module=module)
                result['changed'] = True
                result['companyapp'] = existing_relation
            else:
                result['changed'] = False
                result['message'] = 'Company-application relation not found'
            module.exit_json(**result)
        else:
            module.fail_json(msg=f"Invalid state: {state}")

    except Exception as e:
        module.fail_json(msg=str(e))


def main():
    run_module()


if __name__ == '__main__':
    main()