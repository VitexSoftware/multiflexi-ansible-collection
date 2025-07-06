#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: company_info
short_description: Get information about a company from MultiFlexi

description:
  - Returns information about a company from MultiFlexi using multiflexi-cli.
options:
  name:
    description:
      - The name of the company to look up.
    required: false
    type: str
  slug:
    description:
      - The slug (code) of the company to look up.
    required: false
    type: str
  ic:
    description:
      - The IC of the company to look up.
    required: false
    type: str
author:
  - Vitex (@Vitexus)
"""

EXAMPLES = """
- name: Get company info by name
  company_info:
    name: "demo"
  register: company_info_result

- name: Get company info by slug
  company_info:
    slug: "DEMO"
  register: company_info_result
"""

RETURN = """
company:
    description: Company information or None if not found
    type: dict
    returned: always
    sample:
      id: 1
      name: "demo"
      slug: "DEMO"
      ic: "12345678"
      email: "demo@example.com"
"""

def run_cli_command(args, module=None):
    if module and module._verbosity >= 2:
        module.warn(f"Running CLI command: {' '.join(args)}")
    result = subprocess.run(args, capture_output=True, text=True)
    if module and module._verbosity >= 2:
        module.warn(f"CLI stdout: {result.stdout.strip()}")
        if result.stderr.strip():
            module.warn(f"CLI stderr: {result.stderr.strip()}")
    # Try to parse stdout as JSON, even if returncode != 0
    try:
        data = json.loads(result.stdout)
        return data
    except Exception:
        if result.returncode != 0:
            raise Exception(f"multiflexi-cli error: {result.stderr.strip()}")
        return None

def main():
    module_args = dict(
        name=dict(type='str', required=False),
        slug=dict(type='str', required=False),
        ic=dict(type='str', required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    cli_base = ['multiflexi-cli', 'company', 'get', '--verbose', '--format', 'json']
    if module.params.get('slug'):
        cli_base += ['--slug', module.params['slug']]
    elif module.params.get('ic'):
        cli_base += ['--ic', module.params['ic']]
    elif module.params.get('name'):
        cli_base += ['--name', module.params['name']]
    else:
        module.fail_json(msg="At least one of 'slug', 'ic', or 'name' must be provided.")

    try:
        data = run_cli_command(cli_base, module=module)
        if isinstance(data, dict) and data.get("status") == "not found":
            module.exit_json(changed=False, company=None, msg=data.get("message", "Company not found"))
        module.exit_json(changed=False, company=data)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
