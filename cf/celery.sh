#!/bin/sh

echo "------ Running celery instance -----"
celery worker --app=exchange.celeryapp:app -B -l INFO
