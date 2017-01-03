#!/bin/bash

IP=$(sed -ne "s/config.vm.network :private_network, ip: *[ ]['\"]\([^'\"]*\)['\"] */\1/p" /vagrant/Vagrantfile | tr -d '[[:space:]]')

if [[ $PATH != *"pgsql-9.6"* ]];then
  export PATH=$PATH:/usr/pgsql-9.6/bin
fi

export SITEURL="http://${IP}/"
export ES_URL="http://${IP}:9200/"
export LOCKDOWN_GEONODE=True
export BROKER_URL='amqp://guest:guest@localhost:5672/'
export DATABASE_URL='postgres://exchange:boundless@localhost:5432/exchange'
export POSTGIS_URL='postgis://exchange:boundless@localhost:5432/exchange_data'
export GEOSERVER_URL="http://${IP}/geoserver/"
export GEOSERVER_DATA_DIR='/vagrant/dev/.geoserver/data'
export GEOSERVER_LOG='/vagrant/dev/.geoserver/data/logs/geoserver.log'
export GEOGIG_DATASTORE_DIR='/vagrant/dev/.geoserver/data/geogig'
export STATIC_ROOT='/vagrant/.storage/static_root'
export STATIC_URL='/static/'
export MEDIA_ROOT='/vagrant/.storage/media'
export MEDIA_URL='/media/'
export DEBUG_STATIC='False'
export ALLOWED_HOSTS="['*']"
export LANGUAGE_CODE='en-us'
export SOCIAL_BUTTONS='False'
export SECRET_KEY='exchange@q(6+mnr&=jb@z#)e_cix10b497vzaav61=de5@m3ewcj9%ctc'
export DEFAULT_ANONYMOUS_VIEW_PERMISSION='False'
export DEFAULT_ANONYMOUS_DOWNLOAD_PERMISSION='False'
# export WGS84_MAP_CRS=True
