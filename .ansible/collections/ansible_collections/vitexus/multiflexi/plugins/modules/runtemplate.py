#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: runtemplate
short_description: Manage MultiFlexi run templates
description:
    - This module allows you to create, update, get, and delete run templates in MultiFlexi.
author:
    - Vitex (@Vitexus)
version_added: "1.0.0"
options:
    state:
        description:
            - The desired state of the run template.
        required: true
        type: str
        choices: ['present', 'absent', 'get']
    runtemplate_id:
        description:
            - The ID of the run template.
        required: false
        type: int
    name:
        description:
            - The name of the run template.
        required: false
        type: str
    app_id:
        description:
            - The application ID.
        required: false
        type: int
    app_uuid:
        description:
            - The application UUID.
        required: false
        type: str
    company_id:
        description:
            - The company ID.
        required: false
        type: int
    company:
        description:
            - The company slug/code or ID.
        required: false
        type: str
    active:
        description:
            - Whether the run template is active.
        required: false
        type: bool
    interv:
        description:
            - Interval specification code.
        required: false
        type: str
    cron:
        description:
            - Crontab expression.
        required: false
        type: str
    config:
        description:
            - Application configuration (dictionary).
        required: false
        type: dict
    executor:
        description:
            - Executor to use.
        required: false
        type: str
    schedule_time:
        description:
            - Schedule time for launch (Y-m-d H:i:s or "now").
        required: false
        type: str
"""

EXAMPLES = """
# Create a run template
- name: Create run template
  vitexus.multiflexi.runtemplate:
    state: present
    name: "demo_Test"
    app_uuid: "78fa718c-7ca2-4a38-840e-8e5f0db06432"
    company: "DEMO"
    active: true

# Get a run template
- name: Get run template
  vitexus.multiflexi.runtemplate:
    state: get
    name: "demo_Test"

# Delete a run template
- name: Delete run template
  vitexus.multiflexi.runtemplate:
    state: absent
    runtemplate_id: 1
"""

RETURN = """
runtemplate:
    description: The run template object.
    type: dict
    returned: always
    sample:
        {
            "id": 1,
            "name": "demo_Test",
            "app_id": 1,
            "company_id": 1,
            "active": true
        }
"""


def run_cli(module, args):
    cli = 'multiflexi-cli'
    cmd = [cli] + args + ['--verbose', '--format', 'json']
    # Print command in debug mode
    if hasattr(module, '_verbosity') and module._verbosity >= 2:
        module.warn(f"[DEBUG] Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Print output in debug mode
        if hasattr(module, '_verbosity') and module._verbosity >= 2:
            module.warn(f"[DEBUG] CLI stdout: {result.stdout.strip()}")
            if result.stderr.strip():
                module.warn(f"[DEBUG] CLI stderr: {result.stderr.strip()}")
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        # Check for 'not found' in output, return special marker for caller to handle
        err_output = (e.stdout or '') + (e.stderr or '')
        if 'not found' in err_output.lower():
            if hasattr(module, '_verbosity') and module._verbosity >= 2:
                module.warn(f"[DEBUG] CLI error: {err_output.strip()}")
            return {'_not_found': True, '_cli_error': err_output.strip()}
        try:
            err = json.loads(e.stdout or e.stderr)
        except Exception:
            err = e.stdout or e.stderr
        if hasattr(module, '_verbosity') and module._verbosity >= 2:
            module.warn(f"[DEBUG] CLI error: {err}")
        module.fail_json(msg=f"CLI error: {err}", rc=e.returncode)
    except Exception as e:
        if hasattr(module, '_verbosity') and module._verbosity >= 2:
            module.warn(f"[DEBUG] Failed to run CLI: {e}")
        module.fail_json(msg=f"Failed to run CLI: {e}")


def find_existing_runtemplate(module):
    # Priority: runtemplate_id > name
    # NOTE: run-template:get in multiflexi-cli 2.5.6 only supports --id and --name
    if module.params.get('runtemplate_id'):
        res = run_cli(module, ['run-template:get', '--id', str(module.params['runtemplate_id'])])
        if isinstance(res, dict) and res.get('id'):
            return res
        if isinstance(res, dict) and res.get('_not_found'):
            return None
    elif module.params.get('name'):
        res = run_cli(module, ['run-template:get', '--name', module.params['name']])
        if isinstance(res, dict) and res.get('id'):
            return res
        if isinstance(res, dict) and res.get('_not_found'):
            return None
        # If it returns a list, filter by company if provided
        if isinstance(res, list):
            for tpl in res:
                if module.params.get('company'):
                    # tpl might have company_id or company slug
                    if str(tpl.get('company_id')) == str(module.params['company']) or tpl.get('company_slug') == module.params['company']:
                         return tpl
                elif module.params.get('company_id'):
                    if str(tpl.get('company_id')) == str(module.params['company_id']):
                        return tpl
                else:
                    return tpl # Return first match if no company filter
    return None


def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'absent', 'get']),
        runtemplate_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        app_id=dict(type='int', required=False),
        app_uuid=dict(type='str', required=False),
        company_id=dict(type='int', required=False),
        company=dict(type='str', required=False),
        active=dict(type='bool', required=False),
        interv=dict(type='str', required=False),
        cron=dict(type='str', required=False),
        config=dict(type='dict', required=False),
        executor=dict(type='str', required=False),
        schedule_time=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        runtemplate=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']

    if state == 'get':
        tpl = find_existing_runtemplate(module)
        if tpl:
            result['runtemplate'] = tpl
        else:
            templates = run_cli(module, ['run-template:list'])
            result['runtemplate'] = templates
        module.exit_json(**result)

    elif state == 'present':
        tpl = find_existing_runtemplate(module)
        if tpl:
            # Update
            update_args = ['run-template:update', '--id', str(tpl['id'])]
            changed = False

            # Simple fields
            for field in ['name', 'company_id', 'company', 'active', 'interv', 'cron', 'executor']:
                val = module.params.get(field)
                if val is not None:
                    # Compare
                    current_val = tpl.get(field)
                    if isinstance(val, bool):
                        current_val = bool(current_val)
                    if str(val) != str(current_val if current_val is not None else ''):
                        update_args += [f'--{field}', str(int(val)) if isinstance(val, bool) else str(val)]
                        changed = True

            # Handle config dictionary
            if module.params.get('config'):
                for k, v in module.params['config'].items():
                    update_args += ['--config', f'{k}={v}']
                changed = True

            # Prefer app_uuid over app_id if provided
            if module.params.get('app_uuid'):
                if module.params['app_uuid'] != tpl.get('app_uuid'):
                    update_args += ['--app_uuid', module.params['app_uuid']]
                    changed = True
            elif module.params.get('app_id'):
                if str(module.params['app_id']) != str(tpl.get('app_id')):
                    update_args += ['--app_id', str(module.params['app_id'])]
                    changed = True

            if not changed:
                result['runtemplate'] = tpl
                module.exit_json(**result)

            if module.check_mode:
                result['changed'] = True
                result['runtemplate'] = tpl
                module.exit_json(**result)

            run_cli(module, update_args)
            latest = run_cli(module, ['run-template:get', '--id', str(tpl['id'])])
            result['changed'] = True
            result['runtemplate'] = latest
            module.exit_json(**result)
        else:
            # Create
            create_args = ['run-template:create']
            for field in ['name', 'company_id', 'company', 'active', 'interv', 'cron', 'executor']:
                val = module.params.get(field)
                if val is not None:
                    create_args += [f'--{field}', str(int(val)) if isinstance(val, bool) else str(val)]

            # Handle config dictionary
            if module.params.get('config'):
                for k, v in module.params['config'].items():
                    create_args += ['--config', f'{k}={v}']

            # Prefer app_uuid over app_id if provided
            if module.params.get('app_uuid'):
                create_args += ['--app_uuid', module.params['app_uuid']]
            elif module.params.get('app_id'):
                create_args += ['--app_id', str(module.params['app_id'])]

            if module.check_mode:
                result['changed'] = True
                result['runtemplate'] = None
                module.exit_json(**result)

            created = run_cli(module, create_args)

            # If created is a list (unlikely for create but good to handle), pick the matching one
            tpl_id = None
            if isinstance(created, dict):
                tpl_id = created.get('id')
            elif isinstance(created, list) and len(created) > 0:
                tpl_id = created[0].get('id')

            if tpl_id:
                latest = run_cli(module, ['run-template:get', '--id', str(tpl_id)])
                result['runtemplate'] = latest
            else:
                result['runtemplate'] = created
            result['changed'] = True
            module.exit_json(**result)

    elif state == 'absent':
        tpl = find_existing_runtemplate(module)
        if tpl:
            delete_args = ['run-template:delete', '--id', str(tpl['id'])]
            if module.check_mode:
                result['changed'] = True
                result['runtemplate'] = tpl
                module.exit_json(**result)
            run_cli(module, delete_args)
            result['changed'] = True
            result['runtemplate'] = tpl
            module.exit_json(**result)
        else:
            result['changed'] = False
            result['message'] = 'Runtemplate not found.'
            module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")


def main():
    run_module()


if __name__ == '__main__':
    main()
