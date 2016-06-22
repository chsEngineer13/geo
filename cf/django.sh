#!/bin/sh

echo "------ Create database tables ------"
python manage.py syncdb --noinput
python manage.py collectstatic --noinput
#echo "from geonode.people.models import Profile; Profile.objects.create_superuser('admin', 'exchange@boundlessgeo.com', 'exchange')" | python manage.py shell

echo "------ Running server instance -----"
python manage.py runserver --insecure 0.0.0.0:$PORT
#gunicorn exchange.wsgi --workers 2
