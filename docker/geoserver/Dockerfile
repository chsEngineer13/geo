# Can't use https://github.com/kartoza/docker-geoserver/blob/master/Dockerfile
# because it uses jre7.
FROM tomcat:9-jre8

# Grab the WAR file containing the version of GeoServer Exchange depends on.
# Avoid ADD so we can reuse this layer instead of downloading at every build.
RUN wget --directory-prefix /tmp --progress=dot:giga https://s3.amazonaws.com/boundlessps-public/GVS/geoserver.war

# Run config inside container
RUN unzip -o /tmp/geoserver.war -d /tmp/geoserver && \
    sed -i.bak 's@<baseUrl>\([^<][^<]*\)</baseUrl>@<baseUrl>http://172.16.238.2/</baseUrl>@' \
               /tmp/geoserver/data/security/auth/geonodeAuthProvider/config.xml && \
    rm -rf /usr/local/tomcat/webapps/geoserver && \
    mv /tmp/geoserver $CATALINA_HOME/webapps/geoserver && \
    chmod -R 755 $CATALINA_HOME/webapps/geoserver && \
    rm /tmp/geoserver.war && \
    # Edit context.xml to quiet log spam about cache size
    sed -i'' 's/<\/Context>/<Resources cacheMaxSize="35000" \/><\/Context>/' $CATALINA_HOME/conf/context.xml && \
    # quiet warning since this is not production
    mv $CATALINA_HOME/webapps/geoserver/data/security/masterpw.info $CATALINA_HOME/webapps/geoserver/data/security/masterpw.info.bak
# Add .geogigconfig from outside container
ADD .geogigconfig $CATALINA_HOME/webapps/geoserver/data/geogig/

# TODO: do these need to be moved to /scratch or can we leave them separate?
ENV GEOSERVER_DATA_DIR=$CATALINA_HOME/webapps/geoserver/data
ENV GEOSERVER_LOG=$GEOSERVER_DATA_DIR/logs/geoserver.log
ENV GEOGIG_DATASTORE_DIR=$GEOSERVER_DATA_DIR/geogig
