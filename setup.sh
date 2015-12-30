#!/bin/bash

sudo apt-get update
sudo apt-get install python-setuptools python-dev
sudo easy_install pip
sudo -H pip install virtualenv 
sudo apt-get install postgresql libpq-dev
sudo apt-get install mysql-server libmysqlclient-dev

virtualenv env
source env/bin/activate

pip install -r requirements.txt

deactivate
