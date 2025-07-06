demo:
	ANSIBLE_ROLES_PATH=roles ansible-playbook -vvvvv -i tests/hosts.ini tests/local_demo.yml

describecli:
	multiflexi-cli describe > docs/multiflexi-cli.json

