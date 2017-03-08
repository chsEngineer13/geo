#!/bin/bash

source /env/bin/activate

pip install pytest-cov
export DJANGO_SETTINGS_MODULE='exchange.settings'
export PYTEST=1

python manage.py migrate
python manage.py collectstatic --noinput
#py.test --ignore=tests/ --cov-report html:cov_html --cov=exchange exchange/tests/
py.test -v --ignore=tests/ --cov=exchange exchange/tests/
coverage report -m
