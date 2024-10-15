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
