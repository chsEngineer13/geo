#!/bin/bash

# Include common variables and routines that are also used in worker.sh
HERE=$(dirname $(readlink -f $0))
source "${HERE}/common.sh"
source "/etc/profile.d/vendor-libs.sh"
# path to the log for this shell script - used by log() in common.sh
readonly startup_log="/tmp/exchange_startup.log"

start_django () {
    local django_address="${django_host}:${django_port}"
    log "Starting django on ${django_address}"
    [ ! -f /env/bin/python ] && die "virtualenv not found at /env"
    [ ! -f /mnt/exchange/manage.py ] && die "Exchange not found at /mnt/exchange"
    /env/bin/python /mnt/exchange/manage.py runserver "${django_address}" &
    # set global pid to wait on later
    pid=$!
}

wait_for_django () {
    # Poll via cURL, kill and ping until it's up or definitely down.
    # wait_for_url consumes ${host} and ${pid} as if they were arguments.
    wait_for_url "${name}" "${SITE_URL}"
}

name="django"

# Make a note in the log in case something fails silently in the following
log "Starting Exchange"

# Check that we have the right things mounted and pester the user as needed,
# since it is easy to forget or mess up.
check_mounts

# Clean up *.pyc files which can throw a monkey wrench in the works these can
# persist or transfer between docker/vagrant envs due to the use of mounted
# directories.
remove_pycs

# Set environment variables
load_settings

# Try to ensure we have the latest GeoNode deps installed from requirements.txt
install_dependencies

# We want to run migrations - but wait for PostGIS to come up first, so the
# migrations don't just bomb out with an error.
wait_for_pg "database"
run_migrations

# Now that migrations are done, we can get Django loading.
start_django

# Ensure both GeoServer and Django are up before declaring we're ready to go.
wait_for_django
wait_for_geoserver

log "Exchange is ready on http://172.16.238.2"

# Wait for Django process and propagate its exit status.
started "${name}" "${pid}"
