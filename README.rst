================
geonode-exchange
================

.. image:: https://coveralls.io/repos/github/boundlessgeo/exchange/badge.svg?branch=master
    :target: https://coveralls.io/github/boundlessgeo/exchange?branch=master

.. image:: https://travis-ci.org/boundlessgeo/exchange.svg?branch=master
    :target: https://travis-ci.org/boundlessgeo/exchange

geonode-exchange is a django project built on GeoNode.

---------
Run Tests
---------
Steps to run tests locally:

.. code-block:: bash

   pip install pytest-cov
   export DJANGO_SETTINGS_MODULE='exchange.settings'
   export PYTEST=1
   python manage.py migrate
   python manage.py collectstatic --noinput
   py.test --ignore=tests/ \
           --cov-report html:cov_html \
           --cov=exchange exchange/tests/
