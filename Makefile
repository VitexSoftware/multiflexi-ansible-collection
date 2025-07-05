demo:
	ANSIBLE_ROLES_PATH=roles ansible-playbook -vvvv -i tests/hosts.ini tests/local_demo.yml
