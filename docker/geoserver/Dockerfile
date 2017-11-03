FROM tomcat:latest

# Run config inside container
RUN apt-get update &&\
    apt-get install -y libgeos-dev libproj-dev && \
    wget -O /tmp/geoserver.war --progress=dot:giga https://exchange-development-war.s3-accelerate.amazonaws.com/war/geoserver-2.12.war && \
    unzip -o /tmp/geoserver.war -d /tmp/geoserver && \
    sed -i 's/localhost:8080/172.16.238.2/' /tmp/geoserver/data/global.xml && \
    sed -i 's@localhost:\(8000\|8080\)@172.16.238.2@g' /tmp/geoserver/data/security/filter/geonode-oauth2/config.xml && \
    sed -i 's@localhost:8000@172.16.238.2@g' /tmp/geoserver/data/security/role/geonode\ REST\ role\ service/config.xml && \
    rm -rf /usr/local/tomcat/webapps/geoserver && \
    mv /tmp/geoserver $CATALINA_HOME/webapps/geoserver && \
    chmod -R 755 $CATALINA_HOME/webapps/geoserver && \
    rm -f /tmp/geoserver.war && \
    rm -rf $CATALINA_HOME/webapps/geoserver/data/geofence/geofence_db && \
    # Edit context.xml to quiet log spam about cache size
    sed -i'' 's/<\/Context>/<Resources cacheMaxSize="35000" \/><\/Context>/' $CATALINA_HOME/conf/context.xml && \
    # quiet warning since this is not production
    rm -f $CATALINA_HOME/webapps/geoserver/data/security/masterpw.info

# Add .geogigconfig from outside container
ADD .geogigconfig $CATALINA_HOME/webapps/geoserver/data/geogig/

# TODO: do these need to be moved to /scratch or can we leave them separate?
ENV JAVA_OPTS="-DGEOSERVER_DATA_DIR=$CATALINA_HOME/webapps/geoserver/data -DGEOGIG_DATASTORE_DIR=$GEOSERVER_DATA_DIR/geogig -Dgeofence.dir=$CATALINA_HOME/webapps/geoserver/data/geofence -Dgeofence-ovr=file:$CATALINA_HOME/webapps/geoserver/data/geofence/geofence-datasource-ovr.properties"
