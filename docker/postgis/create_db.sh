#!/bin/bash
set -e

POSTGRES="psql --username ${POSTGRES_USER}"
POSTGIS="psql --username ${POSTGRES_USER} --dbname exchange_data"


$POSTGRES <<EOSQL
CREATE DATABASE exchange OWNER ${DB_USER};
CREATE DATABASE exchange_data OWNER ${DB_USER};
CREATE DATABASE registry R ${DB_USER};
EOSQL

$POSTGIS <<EOSQL
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
GRANT ALL ON geometry_columns TO PUBLIC;
GRANT ALL ON spatial_ref_sys TO PUBLIC;
EOSQL
