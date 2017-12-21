#!/bin/bash

# Code style checks
function lint {
    echo "-------> exchange pycodestyle"
    pycodestyle exchange --ignore=E722,E731
    echo "-------> docker-compose yamllint"
    yamllint -d "{extends: relaxed, rules: {line-length: {max: 120}}}" docker-compose.yml
}

# Jenkins specific function for builds on master branch, requires sonar auth token
function sonar-scan {
    exchange_ver=`grep "__version__ =" exchange/__init__.py | sed "s/__version__ = '\(.*\)'/\1/"`
    echo $exchange_ver
    sonar-scanner -Dsonar.host.url=$SONAR_HOST_URL \
              -Dsonar.login=$SONAR_TOKEN \
              -Dsonar.projectKey=com.boundlessgeo.exchange \
              -Dsonar.sources=exchange \
              -Dsonar.projectVersion=$exchange_ver \
              -Dsonar.projectName=exchange \
              -Dsonar.language=py \
              -Dsonar.python.pylint=/usr/bin/pylint
    sonar-scanner -Dsonar.host.url=$SONAR_HOST_URL \
              -Dsonar.login=$SONAR_TOKEN \
              -Dsonar.projectKey=com.boundlessgeo.geonode \
              -Dsonar.sources=vendor/geonode/geonode \
              -Dsonar.projectVersion=2.6.1 \
              -Dsonar.projectName=geonode \
              -Dsonar.language=py \
              -Dsonar.python.pylint=/usr/bin/pylint
}
