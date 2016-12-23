FROM nginx
RUN mkdir -p /etc/nginx/ssl
ADD ./ssl/nginx.crt /etc/nginx/ssl/
ADD ./ssl/nginx.key /etc/nginx/ssl/
RUN chmod 600 /etc/nginx/ssl/*
ADD exchange.conf /etc/nginx/conf.d/default.conf
ADD 502.html /usr/share/nginx/html/
