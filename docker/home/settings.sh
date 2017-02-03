#!/bin/bash

set -e

# export DJANGO_STATIC_ROOT='/scratch/static_root'
# export DJANGO_MEDIA_ROOT='/scratch/media_root'

if [[ $PATH != *"pgsql-9.6"* ]];then
  export PATH=$PATH:/usr/pgsql-9.6/bin
fi
# TODO: does this need to be a hardcoded IP?
export SITEURL='http://172.16.238.2/'
export ES_URL='http://search:9200/'
export LOCKDOWN_GEONODE=True
export BROKER_URL='amqp://guest:guest@queue:5672/'
export DATABASE_URL='postgres://exchange:boundless@database:5432/exchange'
export POSTGIS_URL='postgis://exchange:boundless@database:5432/exchange_data'
export GEOSERVER_URL='http://172.16.238.2/geoserver/'
export GEOSERVER_DATA_DIR='/scratch/geoserver/data'
export GEOSERVER_LOG='/scratch/geoserver/logs'
export GEOGIG_DATASTORE_DIR='/scratch/geogig/data'

# debug for local dev
export DJANGO_LOG_LEVEL=DEBUG

# allow override by environment variable set in docker-compose
export REGISTRYURL=${REGISTRYURL:-'http://registry.boundlessgeo.io'}
export STATIC_URL='/static/'
export MEDIA_URL='/media/'
export LANGUAGE_CODE='en-us'
export SOCIAL_BUTTONS='False'
export SECRET_KEY='exchange@q(6+mnr&=jb@z#)e_cix10b497vzaav61=de5@m3ewcj9%ctc'
export DEFAULT_ANONYMOUS_VIEW_PERMISSION='False'
export DEFAULT_ANONYMOUS_DOWNLOAD_PERMISSION='False'
# export WGS84_MAP_CRS=True
