FROM centos:6.7

RUN sed -i -e 's:keepcache=0:keepcache=1:' /etc/yum.conf && \
    yum -y install https://s3.amazonaws.com/exchange-development-yum/exchange-development-repo-1.0.0.noarch.rpm  && \
    yum update -y && \
    yum --nogpgcheck -y install registry

EXPOSE 8001

COPY registry-settings.sh /etc/profile.d/registry-settings.sh

RUN /usr/bin/registry-createdb

WORKDIR /scratch
CMD  /opt/registry/registry.sh