#!/bin/bash

# INSTALL {project_name_upper} SYSTEM REQUIREMENTS
#
# REQUIRED SYSTEM: UBUNTU 16.04 LTS
#
# This script is a shortcut to install the {project_name} sytem requirements
# on Ubuntu 16.04 linux systems. It also sets up the Python virtualenv.
#
# Activate the virtual env after installation:
#
#    source ~/.bashrc
#    workon {project_name}
#
# This script is designed to be idempotent--running it multiple times
# should not be a problem.
#

# Configuration Variables
db_user='managr'
db_pass='manager'
db_name='managr_db'
virtualenv_name='managr'

# DO NOT EDIT BEYOND THIS POINT

# Install system requirements
sudo apt-get update
sudo apt-get install gcc redis-server -y

# Install PostgreSQL and configure database and user

# Set up apt repository for Ubuntu 16.04
sudo add-apt-repository 'deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
# End repo set-up for 16.04

# Install Postgres, create database, and grant privs
sudo apt-get install curl gcc postgresql postgresql-server-dev-10 libpq-dev -y
sudo -u postgres createdb $db_name
sudo -u postgres psql -c "CREATE USER $db_user WITH PASSWORD '$db_pass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name to $db_user;"

# Also grant permission to create and drop databases, in order to create a test database
sudo -u postgres psql -c "ALTER USER $db_user CREATEDB;"
sudo -u postgres psql -c "ALTER USER $db_user DROPDB;"

# TODO: Install pyenv (Python 3.7)
# TODO: Install pipenv
# TODO: Install project Python requirements (pipenv install)
