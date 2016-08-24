#!/bin/bash
set -e

LOGFILE=/tmp/zz-init-exchange.log

psql -v ON_ERROR_STOP=1 -L "$LOGFILE" --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER exchange WITH PASSWORD 'boundless';
    CREATE DATABASE exchange OWNER exchange;
    CREATE DATABASE exchange_data OWNER exchange;
EOSQL

psql -v ON_ERROR_STOP=1 -L "$LOGFILE" --username "$POSTGRES_USER" --dbname "exchange_data" <<-EOSQL
    CREATE EXTENSION postgis;
    CREATE EXTENSION postgis_topology;
    GRANT ALL ON geometry_columns TO PUBLIC;
    GRANT ALL ON spatial_ref_sys TO PUBLIC;
EOSQL
