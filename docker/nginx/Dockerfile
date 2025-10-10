FROM nginx:1.25-alpine

# Remove default config
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy our config
COPY conf.d/default.conf /etc/nginx/conf.d/

# Ensure certbot directory exists
RUN mkdir -p /var/www/certbot

EXPOSE 80 443