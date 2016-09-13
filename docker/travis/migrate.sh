#!/usr/bin/env bash
# Run migrations to get initial data into Postgres
# and copy static files (images, etc) to $DJANGO_STATIC_ROOT

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";
source $DIR/exchange-settings.sh;
source $DIR/venv.sh

$CMD makemigrations
$CMD collectstatic --noinput
$CMD migrate account --noinput
$CMD migrate --noinput
$CMD loaddata initial
$CMD migrate account --noinput
