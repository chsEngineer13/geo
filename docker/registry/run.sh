#!/bin/bash

source /etc/profile.d/registry-settings.sh
source /etc/profile.d/vendor-libs.sh
source /env/bin/activate

cd /opt/registry
pip install -r requirements.txt
python registry.py runserver 0.0.0.0:8001
