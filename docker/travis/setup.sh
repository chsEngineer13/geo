#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/common.sh

# collect static
$CMD collectstatic --noinput

# migrations
$CMD migrate account --noinput
$CMD migrate --noinput

# load fixtures
$CMD loaddata default_users
$CMD loaddata base_resources
$CMD loaddata default_oauth_apps
