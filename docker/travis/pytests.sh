#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/common.sh

# set test settings
export DJANGO_SETTINGS_MODULE='exchange.settings'
export PYTEST=1

# migrate and collectstatic
$CMD migrate
$CMD collectstatic --noinput
cd /opt/boundless/exchange

# run tests
PYTEST=True bash -c '/env/bin/py.test --cov exchange exchange/tests/'
bash <(curl -s https://codecov.io/bash) -cF python -t ad26f590-7fc2-4f1a-b3a4-c98b1e9cd039
