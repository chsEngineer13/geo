#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/exchange-settings.sh
source $DIR/venv.sh

$CMD test geonode.tests.smoke --noinput --nocapture --detailed-errors --verbosity=1 --failfast
#$CMD test geonode.people.tests geonode.base.tests geonode.layers.tests geonode.maps.tests geonode.proxy.tests geonode.security.tests geonode.social.tests geonode.catalogue.tests geonode.documents.tests geonode.api.tests geonode.groups.tests geonode.services.tests geonode.geoserver.tests geonode.upload.tests geonode.tasks.tests --noinput --failfast
$CMD test geonode --noinput --detailed-errors --verbosity=1 --failfast
