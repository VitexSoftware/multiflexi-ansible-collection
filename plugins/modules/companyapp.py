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
    cli_base = ['multiflexi-cli', 'companyapp']

    try:
        if state == 'get':
            if module.params.get('relation_id'):
                args = cli_base + ['get', '--id', str(module.params['relation_id']), '--format', 'json', '--verbose']
            else:
                # List all relations if no specific ID
                args = cli_base + ['list', '--format', 'json', '--verbose']
            output = run_cli_command(args, module=module, allow_not_found=True)
            try:
                companyapp = json.loads(output)
                result['companyapp'] = companyapp
            except json.JSONDecodeError:
                result['companyapp'] = None
                result['message'] = 'No relations found or invalid response'
            module.exit_json(**result)
            
        elif state == 'present':
            # Check if relation already exists
            existing_relation = None
            if module.params.get('relation_id'):
                check_args = cli_base + ['get', '--id', str(module.params['relation_id']), '--format', 'json', '--verbose']
                try:
                    output = run_cli_command(check_args, module=module, allow_not_found=True)
                    existing_relation = json.loads(output)
                except:
                    existing_relation = None

            if existing_relation and existing_relation.get('id'):
                # Update existing relation
                update_args = cli_base + ['update', '--id', str(existing_relation['id'])]
                if module.params.get('company_id'):
                    update_args += ['--company_id', str(module.params['company_id'])]
                if module.params.get('app_id'):
                    update_args += ['--app_id', str(module.params['app_id'])]
                elif module.params.get('app_uuid'):
                    update_args += ['--app_uuid', module.params['app_uuid']]
                
                if module.check_mode:
                    result['changed'] = True
                    result['companyapp'] = existing_relation
                    module.exit_json(**result)
                    
                update_args += ['--format', 'json', '--verbose']
                output = run_cli_command(update_args, module=module)
                result['changed'] = True
                try:
                    result['companyapp'] = json.loads(output)
                except json.JSONDecodeError:
                    result['companyapp'] = existing_relation
            else:
                # Create new relation
                create_args = cli_base + ['create']
                if module.params.get('company_id'):
                    create_args += ['--company_id', str(module.params['company_id'])]
                else:
                    module.fail_json(msg='company_id is required for creating company-application relations')
                    
                if module.params.get('app_id'):
                    create_args += ['--app_id', str(module.params['app_id'])]
                elif module.params.get('app_uuid'):
                    create_args += ['--app_uuid', module.params['app_uuid']]
                else:
                    module.fail_json(msg='Either app_id or app_uuid is required for creating company-application relations')
                
                if module.check_mode:
                    result['changed'] = True
                    result['companyapp'] = None
                    module.exit_json(**result)
                    
                create_args += ['--format', 'json', '--verbose']
                try:
                    output = run_cli_command(create_args, module=module, allow_not_found=True)
                    if 'already exists' in output.lower():
                        # Relation already exists, not an error
                        result['changed'] = False
                        result['message'] = 'Company-application relation already exists'
                        # Try to get the existing relation info
                        list_args = cli_base + ['list', '--format', 'json', '--verbose']
                        if module.params.get('company_id'):
                            list_args += ['--company_id', str(module.params['company_id'])]
                        try:
                            list_output = run_cli_command(list_args, module=module)
                            relations = json.loads(list_output)
                            if isinstance(relations, list):
                                for rel in relations:
                                    if (module.params.get('app_uuid') and rel.get('app_uuid') == module.params.get('app_uuid')) or \
                                       (module.params.get('app_id') and rel.get('app_id') == module.params.get('app_id')):
                                        result['companyapp'] = rel
                                        break
                        except:
                            pass
                    else:
                        result['changed'] = True
                        try:
                            result['companyapp'] = json.loads(output)
                        except json.JSONDecodeError:
                            result['message'] = 'Relation created successfully'
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        result['changed'] = False
                        result['message'] = 'Company-application relation already exists'
                    else:
                        raise e
            module.exit_json(**result)
            
        elif state == 'absent':
            if not module.params.get('relation_id'):
                module.fail_json(msg='relation_id is required for deleting company-application relations')
                
            # Check if relation exists
            check_args = cli_base + ['get', '--id', str(module.params['relation_id']), '--format', 'json', '--verbose']
            try:
                output = run_cli_command(check_args, module=module, allow_not_found=True)
                existing_relation = json.loads(output)
            except:
                existing_relation = None
                
            if existing_relation and existing_relation.get('id'):
                if module.check_mode:
                    result['changed'] = True
                    result['companyapp'] = existing_relation
                    module.exit_json(**result)
                    
                delete_args = cli_base + ['delete', '--id', str(module.params['relation_id']), '--format', 'json', '--verbose']
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