# cloud foundry deployment
Environment variables are also stored and passed to the app from the manifest.yml

```yaml
 env:
```

## initial push
```bash
cf push -c "bash cf/init_db.sh" \
        set-env GEONODE_ADMIN_PASSWORD '{ADD PASSWORD}' \
        set-env GS_URL 'http://geoserver.example.io/geoserver/' \
        set-env GS_USER 'admin' \
        set-env GS_PASSWORD '{ADD PASSWORD}' \
        set-env DATABASE_URL 'postgres://username:password@postgres.example.io:5432/database' \
        set-env POSTGIS_URL 'postgres://username:password@postgis.example.io:5432/database' \
        set-env ES_URL 'http://elasticsearch.example.io:9200/' \
        set-env ES_INDEX 'exchange' \
        set-env RABBITMQ_URL 'amqp://username:password@rabbitmq.example.io:5672' \
        set-env AWS_S3_CUSTOM_DOMAIN '' \
        set-env AWS_STORAGE_BUCKET_NAME 's3-bucket-example' \
        set-env AWS_ACCESS_KEY_ID '{ADD KEY}' \
        set-env AWS_SECRET_ACCESS_KEY '{ADD SECRET ACCESS KEY}' \
        set-env AUTH_LDAP 1 \
        set-env AUTH_LDAP_SERVER_URI 'ldaps://ldap.example.io:636' \
        set-env AUTH_LDAP_BIND_PASSWORD '{ADD PASSWORD}' \
        set-env AUTH_LDAP_USER_DN_TEMPLATE 'cn=users,cn=accounts,dc=example,dc=io' \
        set-env LDAP_SEARCH_DN 'cn=users,cn=accounts,dc=example,dc=io' \
        set-env AUTH_LDAP_USER '(uid=%(user))' \
        set-env AUTH_LDAP_BIND_DN 'uid=readonly,cn=sysaccounts,cn=etc,dc=example,dc=io' \
```
__Note:__ this will run the init_db.sh and sync the django database

### Variable Description
+ GEONODE_ADMIN_PASSWORD = Optional, if blank it defaults to 'admin'
+ GS_URL = GeoServer endpoint, needs to end with 'geoserver/''
+ GS_USER = Admin user for accessing GeoServer
+ GS_PASSWORD = Admin password for accessng GeoServer
+ DATABASE_URL = 'postgres://username:password@postgres.example.io:5432/database'
+ POSTGIS_URL = 'postgres://username:password@postgis.example.io:5432/database'
+ ES_URL = Elastic Search URL with port
+ ES_INDEX = Elastic Search index name
+ RABBITMQ_URL = 'amqp://username:password@rabbitmq.example.io:5672'
+ AWS_S3_CUSTOM_DOMAIN = Optional, only use if using a custom domain
+ AWS_STORAGE_BUCKET_NAME = S3 Bucket name
+ AWS_ACCESS_KEY_ID = AWS access key id
+ AWS_SECRET_ACCESS_KEY = AWS secret access key
+ AUTH_LDAP = Optional, if using LDAP set to 1

The following are required if 'set-env AUTH_LDAP = 1'
+ AUTH_LDAP_SERVER_URI = LDAP URI
+ AUTH_LDAP_BIND_PASSWORD = LDAP bind password
+ AUTH_LDAP_USER_DN_TEMPLATE = LDAP distinguished name template
+ LDAP_SEARCH_DN = LDAP search distinguished name
+ AUTH_LDAP_USER = LDAP user
+ AUTH_LDAP_BIND_DN = LDAP binding distinguished name 
