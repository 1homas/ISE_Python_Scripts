# README


## Quick Start

1. Create your Python environment and install necessary Python packages :

    ```bash
    pip install --upgrade pip
    pip install pipenv
    pipenv install --python 3.9
    pipenv install requests
    pipenv shell
    ```

    If you have any problems installing Python or Ansible, see [Installing Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html).


2. Export your credentials for ISE into your shell environment. 

        # ISE REST API Credentials
        export ise_rest_hostname='1.2.3.4'
        export ise_rest_username='admin'
        export ise_rest_password='C1sco12345'
        export ise_verify=false

    You may store these in one or more environment files then load them with the source command:

        source ise_environment.sh

3. These Python scripts typically invoke ISE REST APIs so ensure your ISE node (Primary Administration Node) has the APIs enabled or you may run this script to enable them:

    ise_enable_apis.py

4. Run the other scripts.