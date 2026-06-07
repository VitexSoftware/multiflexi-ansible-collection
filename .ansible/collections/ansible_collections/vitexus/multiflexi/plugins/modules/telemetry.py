#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: telemetry
short_description: Test OpenTelemetry metrics export in MultiFlexi

description:
    - This module allows you to test OpenTelemetry metrics export in MultiFlexi.

author:
    - Vitex (@Vitexus)

options:
    endpoint:
        description:
            - Override OTLP endpoint URL.
        required: false
        type: str
    disable_gauges:
        description:
            - Disable observable gauges (only test counters and histograms).
        required: false
        type: bool
        default: false
    multiflexi_cli_path:
        description:
            - Path to the multiflexi-cli executable.
        required: false
        type: str
        default: 'multiflexi-cli'
"""

EXAMPLES = """
- name: Test telemetry
  telemetry:
    endpoint: "http://localhost:4318/v1/metrics"
"""

RETURN = """
telemetry:
    description: Telemetry test results.
    type: dict
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
        endpoint=dict(type='str', required=False),
        disable_gauges=dict(type='bool', required=False, default=False),
        multiflexi_cli_path=dict(type='str', required=False, default='multiflexi-cli'),
    )

    result = dict(
        changed=False,
        telemetry=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    cli_path = module.params['multiflexi_cli_path']

    try:
        if module.check_mode:
            result['changed'] = True
            module.exit_json(**result)

        args = [cli_path, 'telemetry:test']
        if module.params.get('endpoint'):
            args += ['--endpoint', module.params['endpoint']]
        if module.params.get('disable_gauges'):
            args += ['--disable-gauges']

        output = run_cli_command(args)
        # telemetry:test might not return JSON, handle accordingly
        try:
            result['telemetry'] = json.loads(output)
        except json.JSONDecodeError:
            result['telemetry'] = {"output": output.strip()}
        result['changed'] = True

    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
