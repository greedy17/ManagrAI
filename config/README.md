# Setting up AWS Environment

This process is very similar to setting up a local environment with some extra steps to run application workers more efficiently for a production environment.

1. Launch a new Ubuntu 20.04 LTS EC2 instance

Defaults are fine, except for:
 - Configure 16GB of storage instead of the default 8GB
 - Create a new SSH key for prod (or select an appropriate one)
 - Set SSH Security group to be accessible from only authorized IPs
 - Set HTTP Security group to only be accessible from authorized IPs - later we will make it only accessible from the 'production' security group and load balancer.

2. Create a new Deploy Key in Bitbucket

Visit the repository in Bitbucket, go to Repository Settings > Access Keys
Run `ssh-keygen` from the command line to generate a new key, ex: 'mgr_deploy_key'
Click 'Add Key' in Bitbucket and copy-paste the public key you just generated into BB

3. SSH into the instance and clone the repo

Copy your private deploy key to the ~/.ssh folder on the EC2 instance
Use `chmod 600 ~/.ssh/mgr_deploy_key` to set the correct permissions for the private key
Navigate to the home folder and clone the repo:

    git clone git@bitbucket.org:thinknimble/managr.git

The deploy key should give you read-only access to the repo.

4. Install Pip and Pipenv

    sudo apt-get update
    sudo apt-get install python3-pip
    python3 -m pip install pipenv

5. Install pyenv

    sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

    curl https://pyenv.run | bash

Make sure to follow the instructions so that pyenv is available in the path. Copy the following into your ~/.bashrc and then run `source ~/.bashrc`

    export PATH="/home/ubuntu/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

6. Install the proper version of Python with pyenv

    pyenv install 3.9.1

This will take a while...

7. Create the virtualenv using pipenv

First install system deps (NOTE - installs Redis, too):

    sudo apt-get install libjpeg-dev zlib1g-dev gcc redis-server \
        postgresql postgresql-server-dev-10 libpq-dev \
        postgresql-12 postgresql-client-12 libpq-dev -y

Then install python deps. This should create a virtualenv and install all python deps

    cd ~/managr
    python3 -m pipenv install

8. Set up symlinks

    sudo ln -s /home/ubuntu/managr /opt/managr
    sudo ln -s /home/ubuntu/.local/share/virtualenvs/managr-{hash} /opt/venv

9. Set up nginx

Install nginx

    sudo apt-get install nginx

Make a symlink or copy over the prod.conf

    cd /etc/nginx/sites-available
    sudo ln -s /opt/managr/config/nginx/prod.conf .
    cd ../sites-enabled
    sudo ln -s ../sites-available/prod.conf .
    sudo unlink default

10. Create logs directories

Make sure these directories match the directors in the supervisor and nginx configs

    mkdir /opt/managr/logs

11. Create /run/daphne directory

Django Channels uses Daphne and creates socket files in the /run/daphne directory. Because of permissions issues, this directory can't always be created and must be created manually so that the process can create the socket files it needs

    cd /run
    sudo mkdir daphne

12. Set up supervisor

Install

    sudo apt-get install supervisor

Start the service:

    service supervisor restart

Copy the supervisor task from the repo into supervisor's config directory:

    sudo cp /opt/managr/config/supervisor/managr.conf /etc/supervisor/conf.d

Reread:

    supervisorctl reread



## Setting up other Infrastructure

Set Up Application Load Balancer
 - Request an Automated Certificate through ACM
 - Requires DNS verification, so log into Godaddy to set the CNAME record

Set Up RDS
