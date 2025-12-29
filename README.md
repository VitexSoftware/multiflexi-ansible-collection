# Vitexsoftware Multiflexi Collection

This repository contains the `vitexus.multiflexi` Ansible Collection.

## External requirements

Some modules and plugins require external libraries. Please check the requirements for each plugin or module you use in the documentation to find out which requirements are needed.

### MultiFlexi CLI Requirements

This collection requires **multiflexi-cli version 2.2.0 or newer** to be installed on the target systems.

## Included content

### Roles
* **multiflexi_server** - Install MultiFlexi server on your Debian or Ubuntu server

### Modules
* **company** - Create, update or remove companies in MultiFlexi
* **user** - Manage users in MultiFlexi
* **application** - Manage applications in MultiFlexi
* **runtemplate** - Manage run templates in MultiFlexi
* **job** - Manage jobs in MultiFlexi
* **artifact** - Manage job artifacts in MultiFlexi (list, get, save to file)
* **companyapp** - Manage company-application relations
* **credential** - Manage credentials in MultiFlexi
* **credential_type** - Manage credential types in MultiFlexi
* **topic** - Manage topics in MultiFlexi
* **multiflexi_info** - Gather MultiFlexi system information
* **multiflexi_status** - Get MultiFlexi system status
* **user_data_erasure** - Manage GDPR user data erasure requests
* **token** - Manage authentication tokens
* **prune** - Prune logs and jobs
* **queue** - Manage queues

## Using this collection

```bash
    ansible-galaxy collection install vitexus.multiflexi
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
  - name: vitexus.multiflexi
```

To upgrade the collection to the latest available version, run the following command:

```bash
ansible-galaxy collection install vitexus.multiflexi --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax where `X.Y.Z` can be any [available version](https://galaxy.ansible.com/vitexsoftware/multiflexi):

```bash
ansible-galaxy collection install vitexus.multiflexi:==X.Y.Z
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Release notes

See the [changelog](https://github.com/ansible-collections/REPONAMEHERE/tree/main/CHANGELOG.rst).

## Roadmap

* Initial Functionality - v1.0.0
* Extended Functionality - v1.2.0
* Full functionality - v1.3.0

## More information

<!-- List out where the user can find additional information, such as working group meeting times, slack/IRC channels, or documentation for the product this collection automates. At a minimum, link to: -->

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/devel/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/devel/dev_guide/index.html)
- [Ansible Collections Checklist](https://github.com/ansible-collections/overview/blob/main/collection_requirements.rst)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html)
- [The Bullhorn (the Ansible Contributor newsletter)](https://us19.campaign-archive.com/home/?u=56d874e027110e35dea0e03c1&id=d6635f5420)
- [News for Maintainers](https://github.com/ansible-collections/news-for-maintainers)

## Licensing

MIT

See [LICENSE](https://opensource.org/license/MIT) to see the full text.
