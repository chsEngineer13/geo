#!/bin/sh

PASS="admin"
if [ "$GEONODE_ADMIN_PASSWORD" ]; then
    PASS="$GEONODE_ADMIN_PASSWORD"
fi
PASS = $GEONODE_ADMIN_PASSWORD

echo "-----> Create database tables"
python manage.py migrate --noinput

echo "-----> Create default admin user"
echo "from geonode.people.models import Profile; Profile.objects.create_superuser('admin', 'admin@boundlessgeo.com', '$PASS')" | python manage.py shell

echo "-----> Starting gunicorn"
gunicorn exchange.wsgi --workers 2
