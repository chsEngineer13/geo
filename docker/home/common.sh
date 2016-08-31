# This file is sourced by other scripts. It should not actually do anything
# but set flags, define variables and functions for sourcing by other scripts.

# Ensure we abort execution of scripts on errors
set -e

# Paths to dependencies inside the container, mounted as host-shared volumes 
# Note: these are not named EXCHANGE_HOME and GEONODE_HOME to avoid confusion,
# since those names are used OUTSIDE the container in .env & docker-compose.yml
readonly exchange_dir="/mnt/exchange"
readonly geonode_dir="/mnt/geonode"

# Define where the Django server should bind/listen
readonly django_host=0.0.0.0
readonly django_port=80

# PostGIS information so we can wait on PG to come up or run migrations
readonly postgis_username="exchange"
readonly postgis_password="boundless"
readonly postgis_host="database"
readonly postgis_port="5432"
readonly postgis_db="exchange_data"

# Say something to the user and also log it
log () {
    echo "$(date +'[%T]') $@"
    echo "$(date +'[%Y-%m-%d %T:%N]') $@" >> "${startup_log}"
}

# Just say something to the user, consolidate spaces to allow multiline here
aside () {
    echo "$@" | xargs
}

# Just go away
die () {
    echo "$@"
    exit 1
}

echo_ip () {
    local interface="$1"
    [ -z "${interface}" ] && die "no interface argument passed for echo_ip"
    ip addr show "${1}" | grep 'inet\b' | awk '{print $2}' | cut -d/ -f1
}

load_settings () {
    # Load variables into environment for Django app to consume
    source /etc/profile.d/settings.sh

    # Activate the virtualenv
    source /env/bin/activate

    # Set host and SITE_URL based on Docker IP for use by Django process.
    # This does depend on getting the interface right!
    host="$(echo_ip eth0)"
    if ! ping -c 1 -w 0.1 "${host}" > /dev/null 2>&1; then
        die "Something is majorly messed up, I can't ping myself at '${host}'"
    fi
    export SITE_URL="http://${host}:${django_port}"
    # If you change this code to hardcode the IP instead of getting it inside
    # the container, it MUST match the one hardcoded in docker-compose.yml!
}

check_mounts () {
    local error=0
    if [ ! -d "${geonode_dir}" ] || [ ! -f "${geonode_dir}/setup.py" ]; then
        log "Could not find GeoNode directory at ${geonode_dir}."
        error=1
    fi
    if [ ! -d "${exchange_dir}" ] || [ ! -f "${exchange_dir}/setup.py" ]; then
        log "Could not find Exchange directory at ${exchange_dir}."
        error=1
    fi
    if [ "${error}" -eq 1 ]; then
        aside "
            At the root of your Exchange repository, please edit .env to set
            GEONODE_HOME to the location of a git clone of GeoNode,
            and EXCHANGE_HOME to the location of a git clone of Exchange.

            This is required for docker-compose to know what host directories
            it should mount inside the containers. Without accurate paths
            set in .env, containers will not have any code to run.
            "
        exit 1
    fi
}

install_dependencies () {
    # Unfortunately, this requires write access to $geonode_dir, because pip
    # install -e insists on writing $geonode_dir/GeoNode.egg-info.
    # But we still have to do it in order to ensure dependencies get in.
    /env/bin/pip install --upgrade -e "${geonode_dir}" | grep -v 'Requirement already up-to-date'
}

wait_for_pg () {
    local interval=1
    local timeout=1
    local tries=60
    local started=0
    local name="$1"
    local url="${postgis_host}:${postgis_port}/${postgis_db}"
    log "Waiting for ${name} at ${url} ..."
    for try in $(seq "$tries"); do
        sleep "${interval}"
        # Don't actually need to set username or db, just avoids error messages
        if pg_isready --timeout="${timeout}" --host="${postgis_host}" --port="${postgis_port}" --dbname="${postgis_db}" --username="${postgis_username}" > /dev/null; then
            started=1 
            break
        # Check if host is unreachable
        elif ! ping -c 1 -w 0.1 "${postgis_host}" > /dev/null 2>&1; then
            log "database host ${postgis_host} did not respond to ping"
            break
        fi
    done
    if [ "${started}" -eq 0 ]; then
        log "Stopped waiting for ${name} after ${try} tries"
        exit 1
    fi
    log "${name} is up at ${url}"
}

wait_for_url () {
    local interval=1
    local timeout=1
    local tries=60
    local started=0
    local name="$1"
    local url="$2"
    log "Waiting for ${name} at ${url} ..."
    for try in $(seq "$tries"); do
        sleep "${interval}"
        # Poll for HTTP response
        if curl --max-time 1 --head --fail "${url}" > /dev/null 2>&1 ; then
            started=1
            break
        # If we have a pid, check if process is definitely dead
        elif [ ! -z "${pid}" ] && ! kill -0 "${pid}" 2>/dev/null; then
            log "Stopped waiting for ${name}: PID ${pid} is dead"
            exit 1
            break
        # If we have a host, check if host is not responding to ping
        elif [ ! -z "${host}" ] && ! ping -c 1 -w 0.1 "${host}" > /dev/null 2>&1; then
            log "Stopped waiting for ${name}: host ${host} does not ping"
            exit 1
            break
        fi
    done
    if [ "${started}" -eq 0 ]; then
        log "Stopped waiting for ${name} after ${try} tries"
        exit 1
    fi
    log "${name} is up at ${url}"
}

wait_for_geoserver () {
    wait_for_url "geoserver" "${GEOSERVER_URL}web/"
}

echo_postgis_url () {
    echo "postgis://${postgis_username}:${postgis_password}@${postgis_host}:${postgis_port}/${postgis_db}"
}

run_migrations () {
    # Put together a PostGIS URL for migrations. But we still need to have all
    # the separate components making it up for pg_isready.
    local POSTGIS_URL="$(echo_postgis_url)"

    log "Running migrations against '${POSTGIS_URL}' ..."

    local manage='/env/bin/python /mnt/exchange/manage.py'
    if [ ! -z "${POSTGIS_URL}" ]; then
        pushd /mnt/exchange > /dev/null
        $manage makemigrations
        $manage migrate account --noinput
        $manage migrate --noinput
        log "Collecting static assets ..."
        $manage collectstatic --noinput
        # "hotfix, need to find out why it is not importing the categories"
        $manage loaddata initial
    else
        log "POSTGIS_URL is not set, so migrations cannot run"
        exit 1
    fi
}

started () {
    local name="$1"
    local pid="$2"
    wait "${pid}"
    status=$?
    log "${name}: stopping"
    exit "${status}"
}
