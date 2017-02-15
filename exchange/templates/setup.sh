#!/usr/bin/env bash

# export travis ci specific os env settings
export HOST_IP=`netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'`
#export BROKER_URL="amqp://guest:guest@$HOST_IP:5672/"
#export DATABASE_URL="postgres://exchange:boundless@$HOST_IP:5432/exchange"
#export POSTGIS_URL="postgis://exchange:boundless@$HOST_IP:5432/exchange_data"
export ALLOWED_HOSTS= "['*']"
# source vendor libs and active venv
source /etc/profile.d/vendor-libs.sh
source /env/bin/activate

# global variables
INSTALL_DIR="/opt/boundless/exchange"
CMD="/env/bin/python $INSTALL_DIR/manage.py"

# collect static
$CMD collectstatic --noinput

# migrations
$CMD migrate account --noinput
$CMD migrate --noinput

# load fixtures
$CMD loaddata default_users
$CMD loaddata base_resources
$CMD loaddata default_oauth_apps
