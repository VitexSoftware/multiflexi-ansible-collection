#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json

DOCUMENTATION = """
---
module: multiflexi_info
short_description: Gather MultiFlexi application status facts
description:
  - Runs 'multiflexi-cli appstatus --format=json' and returns its output as Ansible facts prefixed with multiflexi_
author:
  - Vitex (@Vitexus)
version_added: "1.0"
"""

EXAMPLES = """
- name: Gather MultiFlexi facts
  multiflexi_info:
"""

RETURN = """
ansible_facts:
  description: MultiFlexi status facts
  returned: always
  type: dict
  sample:
    multiflexi_version: "1.27.1.860"
    multiflexi_php: "8.2.28"
    multiflexi_os: "Linux"
    multiflexi_memory: 3273576
    multiflexi_companies: 4
    multiflexi_apps: 61
    multiflexi_runtemplates: 10
    multiflexi_topics: 77
    multiflexi_credentials: 4
    multiflexi_credential_types: 4
    multiflexi_database: "mysql Localhost via UNIX socket ..."
    multiflexi_status: "running"
    multiflexi_timestamp: "2025-06-18T13:02:38+00:00"
"""

def main():
    module = AnsibleModule(argument_spec={}, supports_check_mode=True)
    try:
        result = subprocess.run(
            ["multiflexi-cli", "appstatus", "--format=json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        data = json.loads(result.stdout)
        facts = {"multiflexi_" + k: v for k, v in data.items()}
        module.exit_json(changed=False, ansible_facts=facts)
    except subprocess.CalledProcessError as e:
        module.fail_json(msg="Failed to run multiflexi-cli: %s" % e.stderr)
    except Exception as e:
        module.fail_json(msg="Error: %s" % str(e))

if __name__ == '__main__':
    main()