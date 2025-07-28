demo:
	ANSIBLE_ROLES_PATH=roles ansible-playbook -vvvvv --limit demo.multiflexi.eu -i tests/hosts.ini tests/local_demo.yml

debian13:
	ANSIBLE_ROLES_PATH=roles ansible-playbook -v --limit debian13 -i tests/hosts.ini tests/local_demo.yml


describecli:
	multiflexi-cli describe > docs/multiflexi-cli.json

