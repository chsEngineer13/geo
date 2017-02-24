#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/common.sh
cd /opt/boundless/exchange

# run coverage
/env/bin/coveralls debug
