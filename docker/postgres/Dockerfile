# See also:
# https://hub.docker.com/r/mdillon/postgis/~/dockerfile/
# https://github.com/appropriate/docker-postgis/blob/master/initdb-postgis.sh
# https://github.com/docker-library/postgres/blob/fc36c25f8ac352f1fea6d0e7cf8d9bd92a4e720f/9.5/Dockerfile
# https://github.com/docker-library/postgres/blob/fc36c25f8ac352f1fea6d0e7cf8d9bd92a4e720f/9.5/docker-entrypoint.sh
FROM mdillon/postgis:9.6
ADD zz-init-exchange.sh /docker-entrypoint-initdb.d/

# Here we try to bake in the initial data setup, to make boot much faster and
# enable really easy database state resets for development.

# The Postgres Dockerfile defines a VOLUME at /var/lib/postgresql/data, then
# initializes it after boot by running /docker-entrypoint.sh. When we want to
# run that same initialization during build, the VOLUME directive wipes it out
# at runtime (producing e.g. errors about missing a conf file). So we leave
# that VOLUME alone and use a different path that can be baked in, so that we
# can get everything ready at build time and then start up fast for dev.
ENV PGDATA=/var/lib/postgresql/data_docker

# Shut up a warning emitted by docker-entrypoint.sh
ENV POSTGRES_PASSWORD=postgres
# Normally docker-entrypoint.sh hangs at the end, here we pass --version as
# a kludge to keep it from hanging in the foreground during build time.
RUN /docker-entrypoint.sh postgres --version

# Since we already ran docker-entrypoint.sh at startup, it is redundant and
# slow to run it again, so override the ENTRYPOINT from Postgres Dockerfile
ENTRYPOINT []

# Start the service like the entrypoint does after it is done with init
CMD ["gosu", "postgres", "postgres"]
