#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Dvořák Vítězslav <info@vitexsoftware.cz>


from __future__ import absolute_import, division, print_function
import json
import mysql.connector
import sqlite3
# import psycopg2

__metaclass__ = type


DOCUMENTATION = """
---
module: company

short_description: Create, update or delete company in Multiflexi

description:
    - This module allows you to create, update or delete company in Multiflexi

author:
    - Vitex (@Vitexus)

requirements:
    - "python >= 3.9"

version_added: 2.1.0

options:
    name:
        description:
            - The name of the company
        required: true
        type: str
    ico:
        description:
            - The ICO of the company
        required: true
        type: str
    code:
        description:
            - The CODE of the company
        required: true
        type: str
    email:
        description:
            - The email of the company
        required: false
        type: str
    state:
        description:
            - The state of the company
        required: false
        type: str
        choices: ['present', 'absent']
        default: 'present'
    enabled:
        description:
            - The enabled state of the company
        required: false
        type: bool
        default: true
    settings:
        description:
            - The settings of the company
        required: false
        type: str
    logo:
        description:
            - The logo of the company
        required: false
        type: str
    server:
        description:
            - The server of the company
        required: false
        type: int
    rw:
        description:
            - The read/write state of the company
        required: false
        type: bool
    setup:
        description:
            - The setup state of the company
        required: false
        type: bool
    webhook:
        description:
            - The webhook state of the company
        required: false
        type: bool
    customer:
        description:
            - The customer of the company
        required: false
        type: int
"""

EXAMPLES = """
# Create company
- name: Create company
  multiflexi_company:
    name: 'Test Company'
    ico: '12345678'
    code: 'TEST'
    email: 'your@mail.com'

# Update company
- name: Update company
  multiflexi_company:
    name: 'Renamed Company'
    code: 'TEST'
    email: 'fixed@mail.com'

# Delete company
- name: Delete company
  multiflexi_company:
    code: 'TEST'
    state: 'absent'
"""

RETURN = """
company:
    description: The company
    type: dict
    returned: always
    sample:
        {
            "id": 1,
            "name": "Test Company",
            "ico": "12345678",
            "code": "TEST",
            "email": "your@email.com"
        }
"""


from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

class MultiFlexi:
    def __init__(self):
        env_file = '/etc/multiflexi/multiflexi.env'

        # Raise exception if file does not exist
        try:
            with open(env_file):
                pass
        except FileNotFoundError:
            raise Exception(f"File {env_file} does not exist")

        with open(env_file, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                if key == 'DB_CONNECTION':
                    self.db_connection = value
                elif key == 'DB_HOST':
                    self.db_host = value
                elif key == 'DB_PORT':
                    self.db_port = value
                elif key == 'DB_DATABASE':
                    self.db_database = value
                elif key == 'DB_USERNAME':
                    self.db_username = value
                elif key == 'DB_PASSWORD':
                    self.db_password = value
    def getDb(self):
        db_type = self.db_connection
        if db_type == 'mysql':
            return mysql.connector.connect(
                host=self.db_host,
                user=self.db_username,
                password=self.db_password,
                database=self.db_database
            )
        elif db_type == 'sqlite':
            return sqlite3.connect(self.db_database)


#MariaDB [multiflexi]> describe company;
# +-----------+------------------+------+-----+---------+----------------+
# | Field     | Type             | Null | Key | Default | Extra          |
# +-----------+------------------+------+-----+---------+----------------+
# | id        | int(11) unsigned | NO   | PRI | NULL    | auto_increment |
# | enabled   | tinyint(1)       | YES  |     | 0       |                |
# | settings  | text             | YES  |     | NULL    |                |
# | logo      | longtext         | YES  |     | ''      |                |
# | server    | int(11)          | NO   | MUL | 0       |                |
# | name      | varchar(32)      | YES  | MUL | NULL    |                |
# | ic        | varchar(32)      | YES  |     | NULL    |                |
# | company   | varchar(255)     | YES  |     | NULL    |                |
# | rw        | tinyint(1)       | YES  |     | NULL    |                |
# | setup     | tinyint(1)       | YES  |     | 0       |                |
# | webhook   | tinyint(1)       | YES  |     | NULL    |                |
# | DatCreate | datetime         | YES  |     | NULL    |                |
# | DatUpdate | datetime         | YES  |     | NULL    |                |
# | customer  | int(11)          | YES  | MUL | NULL    |                |
# | email     | varchar(64)      | YES  |     | NULL    |                |
# | code      | varchar(10)      | NO   |     |         |                |
# +-----------+------------------+------+-----+---------+----------------+
# 16 rows in set (0.010 sec)


class Company:
    def __init__(self, id, enabled, settings, logo, server, name, ic, company, rw, setup, webhook, DatCreate, DatUpdate, customer, email, code):
        self.id = id
        self.enabled = enabled
        self.settings = settings
        self.logo = logo
        self.server = server
        self.name = name
        self.ic = ic
        self.company = company
        self.rw = rw
        self.setup = setup
        self.webhook = webhook
        self.DatCreate = DatCreate
        self.DatUpdate = DatUpdate
        self.customer = customer
        self.email = email
        self.code = code

    def to_dict(self):
        return {
            "id": self.id,
            "enabled": self.enabled,
            "settings": self.settings,
            "logo": self.logo,
            "server": self.server,
            "name": self.name,
            "ic": self.ic,
            "company": self.company,
            "rw": self.rw,
            "setup": self.setup,
            "webhook": self.webhook,
            "DatCreate": self.DatCreate,
            "DatUpdate": self.DatUpdate,
            "customer": self.customer,
            "email": self.email,
            "code": self.code
        }

"""
Gives you an empty company object.

Returns:
    Company: An empty company object.
"""

def empty_company():
    return Company(None, 0, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

"""
Gives you a company object with the given module parameters.

Args:
    module (AnsibleModule): The Ansible module.

Returns:
    Company: A company object with the given module parameters.
"""

def company_with_module_params(module):
    return Company(
        module.params['id'],
        int(module.params['enabled']),
        module.params['settings'],
        module.params['logo'],
        module.params['server'],
        module.params['name'],
        module.params['ic'],
        module.params['company'],
        module.params['rw'],
        module.params['setup'],
        module.params['webhook'],
        None,
        None,
        module.params['customer'],
        module.params['email'],
        module.params['code']
    )



def run_module():
    """
    Run the Ansible module for managing a company.

    Args:
        id (int, optional): The ID of the company. Defaults to None.
        enabled (bool, optional): Whether the company is enabled. Defaults to True.
        settings (str, optional): The settings of the company. Defaults to None.
        logo (str, optional): The logo of the company. Defaults to None.
        server (int, optional): The server of the company. Defaults to None.
        name (str, optional): The name of the company. Defaults to None.
        ic (str, optional): The IC of the company. Defaults to None.
        company (str, optional): The company. Defaults to None.
        rw (bool, optional): Whether the company has read and write access. Defaults to None.
        setup (bool, optional): Whether the company is set up. Defaults to None.
        webhook (bool, optional): Whether the company has a webhook. Defaults to None.
        customer (int, optional): The customer of the company. Defaults to None.
        email (str, optional): The email of the company. Defaults to None.
        code (str, required): The code of the company.
        state (str, optional): The state of the company. Defaults to 'present'.

    Returns:
        dict: A dictionary containing the result of the module execution.
            - changed (bool): Whether the company was changed.
            - company (dict): The company details.

    Raises:
        AnsibleError: If an error occurs during module execution.
    """
    module_args = dict(
        id=dict(type='int', required=False),
        enabled=dict(type='bool', required=False, default=True),
        settings=dict(type='str', required=False),
        logo=dict(type='str', required=False),
        server=dict(type='int', required=False),
        name=dict(type='str', required=False),
        ic=dict(type='str', required=False),
        company=dict(type='str', required=False),
        rw=dict(type='bool', required=False),
        setup=dict(type='bool', required=False),
        webhook=dict(type='bool', required=False),
        customer=dict(type='int', required=False),
        email=dict(type='str', required=False),
        code=dict(type='str', required=True),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent'])
    )



    result = dict(
        changed=False,
        company=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.params['code'] is None and module.params['id'] is None:
        company = company_with_module_params()  # Create new company
    else:
        company = get_company_by_code(module.params['code'])

    result['company'] = company.to_dict()

    if module.check_mode:
        module.exit_json(**result)

    if module.params['state'] == 'present':
        if company.id is None and create_company(module, company):
            result['changed'] = True
    elif company.id and module.params['state'] == 'absent':
        if delete_company(module, company):
            result['company']['enabled'] = False
            result['state'] = 'absent'
            result['changed'] = True

    module.exit_json(**result)

def create_company(module, company):
    if not company.code:
        code = module.params['code']
        name = module.params['name']
        command = f'multiflexi-cli add company {code} "{name}"'
        rc, out, err =  module.run_command(command)
        if rc == 0:
            try:
                result_json = json.loads(out)
                # Use the parsed JSON as needed
                # For example, assign it to a variable:
                parsed_data = result_json
                company = company_with_module_params(module)
                company.id = parsed_data['id']
                update_company_in_db(module, company)
                return True
            except json.JSONDecodeError:
                # Handle JSON decoding error
                return False
    else:
        return False

def update_company_in_db(module, company):
    db = MultiFlexi().getDb()
    cursor = db.cursor()
    query = f"UPDATE company SET name = '{company.name}', enabled = '{company.enabled}', settings = '{company.settings}', logo = '{company.logo}', server = '{company.server}', ic = '{company.ic}', company = '{company.company}', rw = '{company.rw}', setup = '{company.setup}', webhook = '{company.webhook}', DatUpdate = '{datetime.now()}', customer = '{company.customer}', email = '{company.email}', code = '{company.code}' WHERE id = '{company.id}'"
    cursor.execute(query)
    db.commit()
    cursor.close()
    db.close()

def delete_company(module, company):
    if company.code:
        command = f'multiflexi-cli remove company {company.code}'
        module.run_command(command)
        return True
    else:
        return False

def get_company_by_code(code):
    db = MultiFlexi().getDb()
    cursor = db.cursor()
    query = f"SELECT * FROM company WHERE code = '{code}'"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()

    if result is not None:
        return Company(
            result[0], # id
            result[1], # enabled
            result[2], # settings
            result[3], # logo
            result[4], # server
            result[5], # name
            result[6], # ic
            result[7], # company
            result[8], # rw
            result[9], # setup
            result[12], # webhook
            result[11], # DatCreate
            result[12], # DatUpdate
            result[13], # customer
            result[14], # email
            result[15] # code
        )
    else:
        return Company(None, 0, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

def main():
   run_module()


if __name__ == '__main__':
   main()

