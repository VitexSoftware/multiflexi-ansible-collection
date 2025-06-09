#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>

from ansible.module_utils.basic import AnsibleModule
import requests


def run_module():
    module_args = dict(
        state=dict(type='str', required=True,
                   choices=['present', 'absent', 'get']),
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

    headers = {'Content-Type': 'application/json'}
    auth = (module.params['username'], module.params['password'])
    api_url = module.params['api_url']
    suffix = 'json'

    if module.params['state'] == 'get':
        if module.params['runtemplate_id']:
            url = (
                f"{api_url}/runtemplate/"
                f"{module.params['runtemplate_id']}.{suffix}"
            )
            resp = requests.get(url, auth=auth, headers=headers)
            result['runtemplate'] = resp.json()
        else:
            url = f"{api_url}/runtemplates.{suffix}"
            resp = requests.get(url, auth=auth, headers=headers)
            result['runtemplate'] = resp.json()
        module.exit_json(**result)
    elif module.params['state'] == 'present':
        data = {k: v for k, v in module.params.items()
                if k in [
                    'runtemplate_id', 'name', 'app_id', 'company_id', 'active',
                    'iterv', 'prepared', 'success', 'fail'
                ] and v is not None}
        url = f"{api_url}/runtemplate"
        resp = requests.post(url, auth=auth, headers=headers, json=data)
        result['changed'] = True
        result['runtemplate'] = resp.json()
        module.exit_json(**result)
    elif module.params['state'] == 'absent':
        # No DELETE endpoint in OpenAPI, so just simulate
        result['changed'] = False
        result['message'] = 'Delete not implemented in API.'
        module.exit_json(**result)
    else:
        module.fail_json(msg="Invalid state")


def main():
    run_module()


if __name__ == '__main__':
    main()
