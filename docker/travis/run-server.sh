#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";
source $DIR/exchange-settings.sh;

/env/bin/python /opt/boundless/exchange/manage.py runserver 0.0.0.0:80
