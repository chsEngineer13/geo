#!/bin/bash

set -e

# export DJANGO_STATIC_ROOT='/scratch/static_root'
# export DJANGO_MEDIA_ROOT='/scratch/media_root'

export PATH='/usr/pgsql-9.5/bin':$PATH
# TODO: does this need to be a hardcoded IP?
export SITE_URL='http://172.16.238.2/'
export ES_URL='http://search:9200/'
export LOCKDOWN_GEONODE=True
export BROKER_URL='amqp://guest:guest@queue:5672/'
export DATABASE_URL='postgres://exchange:boundless@database:5432/exchange'
export POSTGIS_URL='postgis://exchange:boundless@database:5432/exchange_data'
export GEOSERVER_URL='http://172.16.238.2/geoserver/'
export GEOSERVER_DATA_DIR='/scratch/geoserver/data'
export GEOSERVER_LOG='/scratch/geoserver/logs'
export GEOGIG_DATASTORE_DIR='/scratch/geogig/data'
# export WGS84_MAP_CRS=True
export REGISTRY=True
