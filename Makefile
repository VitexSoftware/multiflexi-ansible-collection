demo:
	ANSIBLE_ROLES_PATH=roles ansible-playbook -vvvvv --limit demo.multiflexi.eu -i tests/hosts.ini tests/local_demo.yml

debian13:
	ANSIBLE_ROLES_PATH=roles ansible-playbook -v --limit debian13 -i tests/hosts.ini tests/local_demo.yml


describecli:
	multiflexi-cli describe > docs/multiflexi-cli.json


# --- MultiFlexi Debian container helpers ---
MF_CONTAINER ?= multiflexi-debian
MF_IMAGE ?= debian:12

.PHONY: bootstrap-debian shell-debian cli-describe-in-container remove-debian update-debian

# Create or update a Debian container with MultiFlexi CLI + SQLite
bootstrap-debian:
	sh scripts/bootstrap_multiflexi_debian.sh $(MF_CONTAINER) $(MF_IMAGE)

# Update packages and CLI inside the container
update-debian:
	podman exec -it $(MF_CONTAINER) sh -lc "apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y upgrade"

# Open an interactive shell in the container
shell-debian:
	podman exec -it $(MF_CONTAINER) sh

# Regenerate CLI description JSON from inside the container
cli-describe-in-container:
	podman exec -it $(MF_CONTAINER) sh -lc "multiflexi-cli describe --format json" > docs/multiflexi-cli.json

# Remove the Debian container
remove-debian:
	- podman rm -f $(MF_CONTAINER)

