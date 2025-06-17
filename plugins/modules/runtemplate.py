#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json


def run_cli_command(args):
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"multiflexi-cli error: {e.stderr.strip()}")


def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'absent', 'get']),
        runtemplate_id=dict(type='int', required=False),
        name=dict(type='str', required=False),
        app_id=dict(type='int', required=False),
        company_id=dict(type='int', required=False),
        active=dict(type='bool', required=False),
        iterv=dict(type='str', required=False),
        prepared=dict(type='bool', required=False),
        success=dict(type='str', required=False),
        fail=dict(type='str', required=False),
        api_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
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
    cli_base = ['multiflexi-cli', 'runtemplate']

    try:
        if state == 'get':
            if module.params['runtemplate_id']:
                args = cli_base + ['get', '--id', str(module.params['runtemplate_id']), '--format', 'json']
                output = run_cli_command(args)
                result['runtemplate'] = json.loads(output)
            else:
                args = cli_base + ['list', '--format', 'json']
                output = run_cli_command(args)
                result['runtemplate'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'present':
            # If runtemplate_id is provided, update; else, create
            if module.params.get('runtemplate_id'):
                args = cli_base + ['update', '--id', str(module.params['runtemplate_id'])]
                result['changed'] = True
            else:
                args = cli_base + ['create']
                result['changed'] = True
            # Add optional parameters
            for param in ['name', 'app_id', 'company_id', 'active', 'iterv', 'prepared', 'success', 'fail']:
                value = module.params.get(param)
                if value is not None:
                    args += [f'--{param}', str(int(value)) if isinstance(value, bool) else str(value)]
            args += ['--format', 'json']
            output = run_cli_command(args)
            result['runtemplate'] = json.loads(output)
            module.exit_json(**result)
        elif state == 'absent':
            if module.params.get('runtemplate_id'):
                args = cli_base + ['delete', '--id', str(module.params['runtemplate_id']), '--format', 'json']
                output = run_cli_command(args)
                result['changed'] = True
                result['runtemplate'] = json.loads(output)
                module.exit_json(**result)
            else:
                result['changed'] = False
                result['message'] = 'runtemplate_id required for absent state.'
                module.exit_json(**result)
        else:
            module.fail_json(msg="Invalid state")
    except Exception as e:
        module.fail_json(msg=str(e))


def main():
    run_module()


if __name__ == '__main__':
    main()
