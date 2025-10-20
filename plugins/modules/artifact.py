#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>

from __future__ import absolute_import, division, print_function
import subprocess
import json
import os
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = """
---
module: artifact

short_description: Manage job artifacts in Multiflexi

description:
    - This module allows you to list, get, and save job artifacts in Multiflexi

author:
    - Vitex (@Vitexus)

requirements:
    - "python >= 3.9"

version_added: 2.1.0

options:
    state:
        description:
            - The desired operation
        required: false
        type: str
        choices: ['list', 'get', 'save']
        default: 'list'
    id:
        description:
            - The ID of the artifact
        required: false
        type: int
    job_id:
        description:
            - Job ID to filter artifacts by
        required: false
        type: int
    file_path:
        description:
            - File path to save artifact content to (required for save action)
        required: false
        type: str
    fields:
        description:
            - Comma-separated list of fields to display
        required: false
        type: str
"""

EXAMPLES = """
# List all artifacts
- name: List all artifacts
  artifact:
    state: list

# List artifacts for a specific job
- name: List artifacts for job
  artifact:
    state: list
    job_id: 123

# Get specific artifact
- name: Get artifact by ID
  artifact:
    state: get
    id: 456

# Save artifact to file
- name: Save artifact to file
  artifact:
    state: save
    id: 456
    file_path: /tmp/artifact_output.txt
"""

RETURN = """
artifact:
    description: The artifact or list of artifacts
    type: dict or list
    returned: always
    sample:
        {
            "id": 1,
            "job_id": 123,
            "filename": "output.txt",
            "content": "artifact content"
        }
changed:
    description: Whether any changes were made (only true for save operations)
    type: bool
    returned: always
saved_to:
    description: Path where artifact was saved (only for save operations)
    type: str
    returned: when state=save
"""


def run_cli_command(args, module=None):
    # Use module._verbosity if available, else check ANSIBLE_VERBOSITY env var
    verbosity = 0
    if module and hasattr(module, '_verbosity'):
        try:
            verbosity = int(module._verbosity)
        except (TypeError, ValueError):
            verbosity = 0
    else:
        import os
        try:
            verbosity = int(os.environ.get('ANSIBLE_VERBOSITY', '0'))
        except Exception:
            verbosity = 0
    if verbosity >= 2 and module is not None:
        module.warn("[DEBUG] Running command: {}".format(' '.join(args)))
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        if verbosity >= 2 and module is not None:
            module.warn("[DEBUG] CLI output: {}".format(result.stdout.strip()))
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"multiflexi-cli error: {e.stderr.strip()}")


def run_module():
    module_args = dict(
        state=dict(type='str', required=False, default='list', choices=['list', 'get', 'save']),
        id=dict(type='int', required=False),
        job_id=dict(type='int', required=False),
        file_path=dict(type='str', required=False),
        fields=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        artifact=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    state = module.params['state']
    cli_base = ['multiflexi-cli', 'artifact']

    try:
        if state == 'list':
            # List artifacts, optionally filtered by job_id
            args = cli_base + ['list', '--format', 'json']
            
            if module.params.get('job_id'):
                args.extend(['--job_id', str(module.params['job_id'])])
            
            if module.params.get('fields'):
                args.extend(['--fields', module.params['fields']])
            
            output = run_cli_command(args, module=module)
            artifacts = json.loads(output)
            result['artifact'] = artifacts
            
        elif state == 'get':
            # Get specific artifact by ID
            if not module.params.get('id'):
                module.fail_json(msg="id parameter is required for get operation")
            
            args = cli_base + ['get', '--id', str(module.params['id']), '--format', 'json']
            
            if module.params.get('fields'):
                args.extend(['--fields', module.params['fields']])
            
            output = run_cli_command(args, module=module)
            artifact = json.loads(output)
            
            if isinstance(artifact, dict) and artifact.get("status") == "not found":
                module.fail_json(msg=f"Artifact with ID {module.params['id']} not found")
            
            result['artifact'] = artifact
            
        elif state == 'save':
            # Save artifact to file
            if not module.params.get('id'):
                module.fail_json(msg="id parameter is required for save operation")
            if not module.params.get('file_path'):
                module.fail_json(msg="file_path parameter is required for save operation")
            
            file_path = module.params['file_path']
            
            # Check if file already exists
            if os.path.exists(file_path):
                if module.check_mode:
                    result['changed'] = True
                    result['saved_to'] = file_path
                    module.exit_json(**result)
                # File exists, we might overwrite it - this counts as a change
                result['changed'] = True
            else:
                result['changed'] = True
            
            if module.check_mode:
                result['saved_to'] = file_path
                module.exit_json(**result)
            
            args = cli_base + ['save', '--id', str(module.params['id']), '--file', file_path]
            
            output = run_cli_command(args, module=module)
            
            # Verify the file was created
            if os.path.exists(file_path):
                result['saved_to'] = file_path
                # Also get the artifact info for reference
                get_args = cli_base + ['get', '--id', str(module.params['id']), '--format', 'json']
                try:
                    get_output = run_cli_command(get_args, module=module)
                    artifact = json.loads(get_output)
                    result['artifact'] = artifact
                except Exception:
                    # If we can't get artifact info, that's ok, save operation still succeeded
                    pass
            else:
                module.fail_json(msg=f"Failed to save artifact to {file_path}")

    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)


if __name__ == '__main__':
    run_module()