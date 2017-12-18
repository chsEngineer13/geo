#!/bin/bash

set -e

pushd /code
pip install pytest-cov
export DJANGO_SETTINGS_MODULE='exchange.settings'
export PYTEST=1
py.test --junitxml=/code/docker/data/pytest-results.xml \
        --cov-report xml:/code/docker/data/coverage.xml \
        --cov=exchange exchange/tests/ \
        --disable-pytest-warnings
popd
