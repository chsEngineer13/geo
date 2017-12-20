FROM quay.io/boundlessgeo/gdal-py-alpine

EXPOSE 8001

RUN git clone https://github.com/boundlessgeo/registry/ /code/vendor/registry/

WORKDIR /code/vendor/registry/

RUN pip install -r requirements.txt

RUN echo "placemark"
COPY entrypoint.sh /app/entrypoint.sh
COPY registry_mappings_overrides.json /app/registry_mappings_overrides.json

CMD ["/app/entrypoint.sh"]
