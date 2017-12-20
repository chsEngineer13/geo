FROM tomcat:latest

RUN apt-get update \
    && wget -O /tmp/geoserver.war --progress=dot:giga https://exchange-development-war.s3-accelerate.amazonaws.com/war/geoserver-2.12.war \
    && unzip -o /tmp/geoserver.war -d $CATALINA_HOME/webapps/geoserver \
    && chmod -R 755 $CATALINA_HOME/webapps/geoserver \
    && rm -f /tmp/geoserver.war \
    && rm -f $CATALINA_HOME/webapps/geoserver/data/security/masterpw.info \
    && sed -i 's/localhost:8080/nginx/' $CATALINA_HOME/webapps/geoserver/data/global.xml \
    && sed -i 's@http://localhost:8000/o/token/@http://nginx/o/token/@g' \
              $CATALINA_HOME/webapps/geoserver/data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8000/o/authorize/@http://localhost/o/authorize/@g' \
              $CATALINA_HOME/webapps/geoserver/data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8080/geoserver@http://localhost/geoserver@g' \
              $CATALINA_HOME/webapps/geoserver/data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8000/api/o/v4/tokeninfo/@http://nginx/api/o/v4/tokeninfo/@g' \
              $CATALINA_HOME/webapps/geoserver/data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8000/account/logout/@http://nginx/account/logout/@g' \
              $CATALINA_HOME/webapps/geoserver/data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8000@http://nginx@g' \
              $CATALINA_HOME/webapps/geoserver/data/security/role/geonode\ REST\ role\ service/config.xml \
    && sed -i 's/<\/Context>/<Resources cacheMaxSize="35000" \/><\/Context>/' \
              $CATALINA_HOME/conf/context.xml


ENV JAVA_OPTS="-DGEOSERVER_DATA_DIR=$CATALINA_HOME/webapps/geoserver/data -DGEOGIG_DATASTORE_DIR=$GEOSERVER_DATA_DIR/geogig -Dgeofence.dir=$CATALINA_HOME/webapps/geoserver/data/geofence -Dgeofence-ovr=file:$CATALINA_HOME/webapps/geoserver/data/geofence/geofence-datasource-ovr.properties -Dorg.geoserver.rest.DefaultUserGroupServiceName=geonode-oauth2"
