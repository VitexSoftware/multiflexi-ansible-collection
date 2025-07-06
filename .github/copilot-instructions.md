<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

Look to docs/multiflexi-cli.json file for available commands and options.
Use multiflexi-cli to interact with MultiFlexi.

Mind the idempotency (updates only if it differs).
Use ansible.builtin.debug to print variables and results for debugging.
Use ansible.builtin.assert to check conditions and ensure correctness.
Use ansible.builtin.fail to handle errors gracefully.
Use ansible.builtin.include_tasks to modularize tasks.
Use ansible.builtin.set_fact to create or update variables dynamically.
Use ansible.builtin.register to capture results of tasks.
Use ansible.builtin.when to conditionally execute tasks based on variable values.
