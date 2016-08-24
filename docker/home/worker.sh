#!/bin/bash

# Include common variables and routines that are also used in exchange.sh 
HERE=$(dirname $(readlink -f $0))
source "${HERE}/common.sh"

# path to the log for this shell script - used by log() in common.sh
readonly startup_log="/tmp/worker_startup.log"

start_worker () {
    # TODO: disable pickle to reduce screaming in startup log w/o C_FORCE_ROOT
    cd /mnt/exchange
    C_FORCE_ROOT=1 /env/bin/celery worker --app=exchange.celery_app:app -B --loglevel INFO &
    pid=$!
}

name="Worker"
log "Starting ${name}"

check_mounts
load_settings
install_dependencies
wait_for_pg "database"
wait_for_url "exchange" "http://exchange"
start_worker
started "celery" "${pid}"
