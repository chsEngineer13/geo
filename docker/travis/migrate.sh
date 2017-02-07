#!/usr/bin/env bash
# Run migrations to get initial data into Postgres
# and copy static files (images, etc) to $DJANGO_STATIC_ROOT

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";
source $DIR/exchange-settings.sh;
source $DIR/venv.sh
source /etc/profile.d/vendor-libs.sh

$CMD collectstatic --noinput
$CMD migrate account --noinput
$CMD migrate --noinput
$CMD loaddata default_users
$CMD loaddata base_resources
$CMD loaddata default_oauth_apps
