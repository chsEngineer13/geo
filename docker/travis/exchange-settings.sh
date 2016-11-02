# These environment variables override defaults
# found in exchange/settings/default.py

export HOST_IP=`netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'`
# export DJANGO_LOG_LEVEL=DEBUG
export ES_URL="http://$HOST_IP:9200/"
export BROKER_URL="amqp://guest:guest@$HOST_IP:5672/"
export SITE_URL=http://127.0.0.1:8000
export DATABASE_URL="postgres://exchange:boundless@$HOST_IP:5432/exchange"
export POSTGIS_URL="postgis://exchange:boundless@$HOST_IP:5432/exchange_data"
