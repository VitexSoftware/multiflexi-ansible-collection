<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

All module logic must be idempotent: modules should only create or update resources if the desired state differs from the current state. If the resource already matches the requested parameters, the module must do nothing and report changed: false. This ensures safe, repeatable automation and prevents unnecessary changes or side effects.

when create new record, use "multiflexi-cli <command> get ..." first to check if the record already exists. If it does not exist, then use "multiflexi-cli <command> create ..." to create the record. If it exists, then use "multiflexi-cli <command> update ..." to update the record.

Use multiflexi-cli to interact with MultiFlexi.

Look to docs/multiflexi-cli.json file for available commands and options.

Use ansible.builtin.debug to print variables and results for debugging.
Use ansible.builtin.assert to check conditions and ensure correctness.
Use ansible.builtin.fail to handle errors gracefully.
Use ansible.builtin.include_tasks to modularize tasks.
Use ansible.builtin.set_fact to create or update variables dynamically.
Use ansible.builtin.register to capture results of tasks.
Use ansible.builtin.when to conditionally execute tasks based on variable values.

in ansible debug mode print all multiflexi-cli commands and their output.

Do not use MultiFlexi online API.
