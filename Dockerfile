# This Dockerfile defines how to build container images containing a
# *development* version of Exchange. It really isn't usable for production, and
# it isn't meant to be; it's for the benefit of people hacking on Exchange.

# The django app is tested on CentOS 6.7 to match client production environment
FROM centos:6.7

# Set up to use the internal yum repo.
# It's normally better practice to use e.g. curl or wget instead of ADD
# to avoid doing the download at every build.
# But in this case, we do want every build to check for changes in
# geoshape.repo, because if it changed then it's possible that the effect of
# the yum installs will change, so that we can't safely reuse the yum installs.
# If geoshape.repo didn't change, the yum installs won't be repeated.
ADD https://yum.boundlessps.com/geoshape.repo /etc/yum.repos.d/

# Prevent yum from invalidating cache every build (default is keepcache=0).
# Pull in initial updates, e.g. security updates
# Install the packages we want for the application
# ... and do one big step to avoid creating extra layers uselessly
# TODO: audit what is needed here or not
RUN sed -i -e 's:keepcache=0:keepcache=1:' /etc/yum.conf && \
    yum -y install https://yum.postgresql.org/9.6/redhat/rhel-6-x86_64/pgdg-centos96-9.6-3.noarch.rpm && \
    yum -y install https://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm && \
    yum update -y && \
    yum -y install \
        # for pip install from git URLs
        git \
        # headers
        python27-devel \
        # create virtualenv
        python27-virtualenv \
        # compile C extensions
        gcc \
        gcc-c++ \
        make \
        expat-devel \
        db4-devel \
        gdbm-devel \
        sqlite-devel \
        readline-devel \
        zlib-devel \
        bzip2-devel \
        openssl-devel \
        tk-devel \
        gdal-devel-2.1.2 \
        libxslt-devel \
        libxml2-devel \
        libjpeg-turbo-devel \
        zlib-devel \
        libtiff-devel \
        freetype-devel \
        lcms2-devel \
        proj-devel \
        geos-devel \
        # Headers for pip install psycopg2
        postgresql96-devel \
        openldap-devel \
        libmemcached-devel \
    && \
    # Create the virtualenv the app will run in
    /usr/local/bin/virtualenv /env && chmod -R 755 /env

# Add Exchange requirements list to pip install during container build.
# All work done AFTER this line will be re-done when requirements.txt changes.
ADD requirements.txt /mnt/exchange/

# Pre-install dependencies
# Get preinstalled GeoNode out of the way so the mount can be used
RUN PATH=$PATH:/usr/pgsql-9.6/bin && /env/bin/pip install -r /mnt/exchange/requirements.txt && \
    /env/bin/pip uninstall -y GeoNode

# docker/home contains a number of things that will go in $HOME:
# - local_settings.py: env-specific monkeypatches for django's settings.py
# - .bash_profile: for activating the virtualenv at login
# - exchange.sh: commands to run at container boot for Exchange Django app
# - worker.sh: commands to run at container boot for Exchange Celery app
# - settings.sh: environment variables
ADD docker/home/* /root/
RUN chmod 755 /root/*.sh /root/*.py

# Relocate files that are expected to be in other places
RUN mv /root/local_settings.py /env/lib/python2.7/site-packages && \
    mv /root/settings.sh /etc/profile.d/

# this will symlink the maploom files to the MapLoom repository which
#  exists outside of the container.
RUN rm -rf /env/lib/python2.7/site-packages/maploom/static/maploom && \ 
    ln -s /mnt/maploom/build /env/lib/python2.7/site-packages/maploom/static/maploom && \
    rm /env/lib/python2.7/site-packages/maploom/templates/maps/maploom.html && \
    ln -s /mnt/maploom/build/maploom.html /env/lib/python2.7/site-packages/maploom/templates/maps/maploom.html

WORKDIR /scratch
CMD ["/root/exchange.sh"]
