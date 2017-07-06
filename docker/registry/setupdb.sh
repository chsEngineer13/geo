#!/bin/bash

source /etc/profile.d/registry-settings.sh
source /etc/profile.d/vendor-libs.sh
source /env/bin/activate

cd /opt/registry

python registry.py pycsw -c setup_db
