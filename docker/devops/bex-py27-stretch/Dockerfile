# quay.io/boundlessgeo/bex-py27-stretch
# docker build -t bex-py27-stretch .
FROM python:2-stretch
LABEL maintainer="Daniel Berry <dberry@boundlessgeo.com>"

ENV CPATH "$CPATH:/usr/include/gdal:/usr/include"

RUN apt-get update \
    && apt-get install -y build-essential \
                          gcc \
                          gdal-bin \
                          libgdal-dev \
                          libxslt1-dev \
                          libldap2-dev \
                          libsasl2-dev \
                          proj-bin \
                          proj-data \
                          python-setuptools \
    && pip install GDAL==2.1.0 \
                   numpy==1.13.3 \
                   python-ldap==2.4.45 \
                   git+https://github.com/boundlessgeo/sphinx@bex#egg=Sphinx

CMD ["/bin/bash"]
