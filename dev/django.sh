#!/bin/bash

source /vagrant/dev/settings.sh
cd /vagrant
source .venv/bin/activate
/vagrant/.venv/bin/python manage.py runserver 0.0.0.0:8000
