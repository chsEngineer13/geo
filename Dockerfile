FROM quay.io/boundlessgeo/bex-py27-stretch

ARG dev

WORKDIR /code

COPY . .

COPY requirements.txt /app/requirements.txt

RUN if [ $dev ] ; then \
      echo "Dev Setup" \
      && sed -i "/egg=geonode/d" /app/requirements.txt \
      && echo "-e /code/vendor/geonode" >> /app/requirements.txt ; \
    fi \
    && sed -i "/GDAL/d" /app/requirements.txt \
    && sed -i "/numpy/d" /app/requirements.txt \
    && sed -i "/python-ldap/d" /app/requirements.txt \
    && pip install -r /app/requirements.txt

COPY docker/exchange/entrypoint.sh /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
