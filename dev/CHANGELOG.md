### 2016-05-22

* *Upgraded to use GeoNode 2.4, Django 1.8.7*

    Exchange now uses native Django migrations to initialize its database.

To initialize against a new/empty database instance, do the following
one-time migration steps:

```bash
$ python manage.py makemigrations
$ python manage.py migrate account --noinput
$ python manage.py migrate --noinput
```

Once migrations are complete, continue with usage as normal.


