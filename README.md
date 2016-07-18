# Boundless Exchange Python Module
Boundless Exchange is a web-based platform for your content, built for your enterprise. It facilitates the creation, sharing, and collaborative use of geospatial data. For power users, advanced editing capabilities for versioned workflows via the web browser are included. Boundless Exchange is powered by GeoNode, GeoGig, OpenLayers, PostGIS and GeoServer. Boundless Exchange is designed as a platform for collaboration. You can now focus on your community – getting stakeholders quickly involved and empowering them with information. Exchange supports communal editing – allowing you to crowd-source information in an online, powerful, distributed/versioned architecture with an intuitive user interface.

## Clone
git clone https://github.com/boundlessgeo/exchange.git

git submodule update --init

### Environment Variables
- SITE_URL
Default: 'http://127.0.0.1:8000'
- LOCKDOWN_GEONODE
Default: None
- GEOSERVER_URL
Default: 'http://127.0.0.1:8080/geoserver/'
- GEOSERVER_USER
Default: 'admin'
- GEOSERVER_PASSWORD
Default: 'geoserver'
- GEOSERVER_LOG
Default: '/var/lib/geoserver_data/logs/geoserver.log'
- GEOSERVER_DATA_DIR
Default: '/var/lib/geoserver_data'
- GEOGIG_DATASTORE_DIR
Default: '/var/lib/geoserver_data/geogig'
- DATABASE_URL
Default: 'development.db'
- POSTGIS_URL
Default: None
- WGS84_MAP_CRS
Default: None
- ES_URL
Default: 'http://127.0.0.1:9200/'
- BROKER_URL
Default: 'amqp://guest:guest@localhost:5672/'
- AUTH_LDAP_SERVER_URI
Default: None
- LDAP_SEARCH_DN
Default: None
- AUTH_LDAP_USER
Default: '(uid=%(user)s)'
- AUTH_LDAP_BIND_DN
Default: ''
- AUTH_LDAP_BIND_PASSWORD
Default: ''
- REGISTRY
Default: None
