#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json


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
    if module.params.get('runtemplate_id'):
        res = run_cli(module, ['runtemplate', 'get', '--id', str(module.params['runtemplate_id'])])
        if isinstance(res, dict) and res.get('id'):
            return res
    elif module.params.get('name'):
        res = run_cli(module, ['runtemplate', 'get', '--name', module.params['name']])
        if isinstance(res, dict) and res.get('id'):
            return res
    return None


def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'absent', 'get']),
        runtemplate_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        app_id=dict(type='int', required=False),
        app_uuid=dict(type='str', required=False),
        company_id=dict(type='int', required=False),
        company=dict(type='str', required=False),  # <-- new option
        active=dict(type='bool', required=False),
        iterv=dict(type='str', required=False),
        prepared=dict(type='bool', required=False),
        success=dict(type='str', required=False),
        fail=dict(type='str', required=False),
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
            templates = run_cli(module, ['runtemplate', 'list'])
            result['runtemplate'] = templates
        module.exit_json(**result)

    elif state == 'present':
        tpl = find_existing_runtemplate(module)
        if tpl:
            # Update
            update_args = ['runtemplate', 'update', '--id', str(tpl['id'])]
            for field in ['name', 'company_id', 'company', 'active', 'iterv', 'prepared', 'success', 'fail']:
                val = module.params.get(field)
                if val is not None:
                    update_args += [f'--{field}', str(int(val)) if isinstance(val, bool) else str(val)]
            # Prefer app_uuid over app_id if provided
            if module.params.get('app_uuid'):
                update_args += ['--app_uuid', module.params['app_uuid']]
            elif module.params.get('app_id'):
                update_args += ['--app_id', str(module.params['app_id'])]
            if module.check_mode:
                result['changed'] = True
                result['runtemplate'] = tpl
                module.exit_json(**result)
            run_cli(module, update_args)
            latest = run_cli(module, ['runtemplate', 'get', '--id', str(tpl['id'])])
            result['changed'] = True
            result['runtemplate'] = latest
            module.exit_json(**result)
        else:
            # Create
            create_args = ['runtemplate', 'create']
            for field in ['name', 'company_id', 'company', 'active', 'iterv', 'prepared', 'success', 'fail']:
                val = module.params.get(field)
                if val is not None:
                    create_args += [f'--{field}', str(int(val)) if isinstance(val, bool) else str(val)]
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
            tpl_id = created.get('id')
            if tpl_id:
                latest = run_cli(module, ['runtemplate', 'get', '--id', str(tpl_id)])
                result['runtemplate'] = latest
            else:
                result['runtemplate'] = created
            result['changed'] = True
            module.exit_json(**result)

    elif state == 'absent':
        tpl = find_existing_runtemplate(module)
        if tpl:
            delete_args = ['runtemplate', 'delete', '--id', str(tpl['id'])]
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
