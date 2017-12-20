#!/bin/bash

registry='python /code/vendor/registry/registry.py'

if [[ ! -f /tmp/registry.db ]]; then
  $registry pycsw -c setup_db
fi

$registry runserver 0.0.0.0:8001
