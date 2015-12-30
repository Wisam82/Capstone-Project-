#!/bin/bash

sudo service mysql start
sudo service postgresql start
source env/bin/activate
python group13.py