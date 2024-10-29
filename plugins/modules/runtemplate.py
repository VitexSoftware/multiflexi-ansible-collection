#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
---
module: runtemplate

short_description: Manage RunTemplate in Multiflexi

description:
    - This module allows you to create or delete RunTemplate in Multiflexi

author:
    - Vitex (@Vitexus)

requirements:
    - "python >= 3.9"

version_added: 2.1.0

options:
    state:
        description:
            - The state of the RunTemplate
        required: true
        type: str
        choices: ['present', 'absent']
    company:
        description:
            - The company associated with the RunTemplate
        required: true
        type: str
    application:
        description:
            - The application associated with the RunTemplate
        required: true
        type: str
    interval:
        description:
            - The interval for the RunTemplate
        required: true
        type: str
    config:
        description:
            - The configuration for the RunTemplate
        required: true
        type: dict
    name:
        description:
            - The name of the RunTemplate
        required: true
        type: str
"""

EXAMPLES = """
# Create RunTemplate
- name: Create RunTemplate
  runtemplate:
    state: 'present'
    company: 'ExampleCompany'
    application: 'ExampleApp'
    interval: 'daily'
    config: {'key': 'value'}
    name: 'ExampleTemplate'

# Delete RunTemplate
- name: Delete RunTemplate
  runtemplate:
    state: 'absent'
    company: 'ExampleCompany'
    application: 'ExampleApp'
    name: 'ExampleTemplate'
"""

RETURN = """
runtemplate:
    description: The RunTemplate
    type: dict
    returned: always
    sample:
        {
            "state": "present",
            "company": "ExampleCompany",
            "application": "ExampleApp",
            "interval": "daily",
            "config": {"key": "value"},
            "name": "ExampleTemplate"
        }
"""

def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'absent']),
        company=dict(type='str', required=True),
        application=dict(type='str', required=True),
        interval=dict(type='str', required=True),
        config=dict(type='dict', required=True),
        name=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    company = module.params['company']
    application = module.params['application']
    interval = module.params['interval']
    config = module.params['config']
    name = module.params['name']

    # Placeholder for actual implementation
    if state == 'present':
        result['changed'] = True
        result['message'] = f"RunTemplate '{name}' for application '{application}' in company '{company}' with interval '{interval}' has been defined."
    elif state == 'absent':
        result['changed'] = True
        result['message'] = f"RunTemplate '{name}' for application '{application}' in company '{company}' has been removed."

    if module.check_mode:
        module.exit_json(**result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
