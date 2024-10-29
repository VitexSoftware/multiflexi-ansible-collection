#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>


DOCUMENTATION = """
---
module: application

short_description: Manage applications in Multiflexi

description:
    - This module allows you to assign or remove applications to/from companies in Multiflexi.

author:
    - Vitex (@Vitexus)

requirements:
    - "python >= 3.9"

version_added: "2.1.0"

options:
    state:
        description:
            - The state of the application.
        required: true
        type: str
        choices: ['present', 'absent']
    company:
        description:
            - The company associated with the application.
        required: true
        type: str
    code:
        description:
            - The code of the application.
        required: true
        type: str
    application:
        description:
            - The name of the application.
        required: true
        type: str
"""

EXAMPLES = """
    - name: Assign application to company
      vitexus.multiflexi.application:
        state: present
        company: ExampleCompany
        code: APP123
        application: ExampleApp

    - name: Remove application from company
      vitexus.multiflexi.application:
        state: absent
        company: ExampleCompany
        code: APP123
        application: ExampleApp
"""

RETURN = """
    message:
        description: The output message that the module generates.
        type: str
        returned: always
    changed:
        description: Whether the application was changed.
        type: bool
        returned: always
"""


from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        state=dict(type='str', required=True, choices=['present', 'absent']),
        company=dict(type='str', required=True),
        code=dict(type='str', required=True),
        application=dict(type='str', required=True)
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
    code = module.params['code']
    application = module.params['application']

    # Implement your logic here
    if state == 'present':
        result['changed'] = True
        result['message'] = f"Application {application} assigned to company {company} with code {code}."
    elif state == 'absent':
        result['changed'] = True
        result['message'] = f"Application {application} removed from company {company} with code {code}."

    if module.check_mode:
        module.exit_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
