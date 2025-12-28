# vim: set tabstop=8 softtabstop=8 noexpandtab:
.PHONY: help demo debian13 describecli bootstrap-debian shell-debian cli-describe-in-container remove-debian update-debian

help: ## Displays this list of targets with descriptions
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}'

demo: ## Run demo playbook against demo.multiflexi.eu with verbose output
	ANSIBLE_ROLES_PATH=roles ansible-playbook -vvvvv --limit demo.multiflexi.eu -i tests/hosts.ini tests/local_demo.yml

debian13: ## Run playbook against debian13 host with moderate verbosity
	ANSIBLE_ROLES_PATH=roles ansible-playbook -v --limit debian13 -i tests/hosts.ini tests/local_demo.yml

describecli: ## Save current multiflexi-cli command description to docs/multiflexi-cli.json
	multiflexi-cli describe > docs/multiflexi-cli.json

# --- MultiFlexi Debian container helpers ---
MF_CONTAINER ?= multiflexi-debian
MF_IMAGE ?= debian:12

bootstrap-debian: ## Bootstrap a Debian container with MultiFlexi CLI and SQLite
	sh scripts/bootstrap_multiflexi_debian.sh $(MF_CONTAINER) $(MF_IMAGE)

update-debian: ## Update all packages and MultiFlexi CLI in the container
	podman exec -it $(MF_CONTAINER) sh -lc "apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y upgrade"

shell-debian: ## Open a shell session inside the MultiFlexi Debian container
	podman exec -it $(MF_CONTAINER) sh

cli-describe-in-container: ## Update docs/multiflexi-cli.json using CLI inside the container
	podman exec -it $(MF_CONTAINER) sh -lc "multiflexi-cli describe --format json" > docs/multiflexi-cli.json

remove-debian: ## Force remove the MultiFlexi Debian container
	podman rm -f $(MF_CONTAINER)

