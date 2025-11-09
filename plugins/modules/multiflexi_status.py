#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: multiflexi_status
short_description: Get MultiFlexi system status

description:
    - This module retrieves comprehensive MultiFlexi system status including database configuration, 
      system services, entity counts, Zabbix monitoring, and OpenTelemetry telemetry configuration.

author:
    - Vitex (@Vitexus)

options:
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'

"""

EXAMPLES = """
- name: Get MultiFlexi system status
  multiflexi_status:

- name: Get MultiFlexi status with custom CLI path
  multiflexi_status:
    multiflexi_cli_path: '/usr/local/bin/multiflexi-cli'
"""

RETURN = """
status:
    description: Complete MultiFlexi system status information.
    type: dict
    returned: always
    contains:
        database:
            description: Database configuration and status
            type: dict
        services:
            description: System services status
            type: dict
        entities:
            description: Count of various MultiFlexi entities
            type: dict
        monitoring:
            description: Zabbix monitoring configuration
            type: dict
        telemetry:
            description: OpenTelemetry configuration
            type: dict
msg:
    description: A message describing the status check.
    type: str
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
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        status=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    cli_path = module.params['multiflexi_cli_path']
    cli_base = [cli_path, 'status']

    try:
        args = cli_base + ['--format', 'json']
        output = run_cli_command(args)
        result['status'] = json.loads(output)
        result['msg'] = "Retrieved MultiFlexi system status"
            
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()