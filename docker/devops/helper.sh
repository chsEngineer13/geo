#!/bin/bash

# Linter
function lint {
    echo "-------> exchange pycodestyle"
    pycodestyle --show-source --show-pep8 exchange
    echo "-------> docker-compose yamllint"
    yamllint -d relaxed docker-compose.yml
}

# Jenkins Specific function for builds on master branch, requires sonar auth token
function sonar-scan {
    for f in `find . -type f -name "setup.py"`  ; do (pushd `dirname $f` \
       && NAME=`grep name setup.py | cut -f2 -d'=' | sed "s|[',]||g"` \
       && sonar-scanner -Dsonar.host.url=$SONAR_HOST_URL \
                        -Dsonar.login=$SONAR_TOKEN \
                        -Dsonar.projectKey=com.boundlessgeo.bex:$NAME \
                        -Dsonar.sources=. \
                        -Dsonar.projectVersion=1.0 \
                        -Dsonar.projectName=$NAME \
                        -Dsonar.language=py \
                        -Dsonar.python.pylint=/usr/bin/pylint \
       && popd \
       || popd); done
    mvn clean install sonar:sonar -Dsonar.host.url=$SONAR_HOST_URL -Dsonar.login=$SONAR_TOKEN
}
