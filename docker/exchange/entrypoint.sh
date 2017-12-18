#!/bin/bash

set -e

maploom_static='/usr/local/lib/python2.7/site-packages/maploom/static/maploom'
maploom_html='/usr/local/lib/python2.7/site-packages/maploom/templates/maps/maploom.html'
manage='python /code/manage.py'

pip freeze

if [[ $TASK != 'worker' ]]; then
  if [[ $MAPLOOM_DEV == 1 ]]; then
    rm -rf $maploom_static
    mkdir -p /usr/local/lib/python2.7/site-packages/maploom/templates/maps
    ln -s /code/vendor/maploom/build $maploom_static
    ln -s /code/vendor/maploom/build/maploom.html $maploom_html
  fi
  # let the db intialize
  sleep 15
  until $manage migrate account --noinput; do
    >&2 echo "db is unavailable - sleeping"
    sleep 5
  done
  # todo: remove this when registry is removed
  until curl -XPUT "registry:8001/catalog/registry/csw"; do
    >&2 echo "registry is unavailable - sleeping"
    sleep 5
  done
  $manage migrate --noinput
  $manage collectstatic --noinput
  $manage loaddata default_users
  $manage loaddata base_resources
  $manage loaddata /code/docker/exchange/docker_oauth_apps.json
  $manage runserver 0.0.0.0:8000
else
  C_FORCE_ROOT=1 celery worker --app=exchange.celery_app:app -B --loglevel DEBUG
fi