FROM nginx:alpine
LABEL maintainer="Daniel Berry <dberry@boundlessgeo.com>"

RUN apk update &&\
    apk add --no-cache ca-certificates curl

COPY ./ssl/* /etc/nginx/ssl/
RUN chmod 400 /etc/nginx/ssl/*
COPY nginx.conf /etc/nginx/nginx.conf
