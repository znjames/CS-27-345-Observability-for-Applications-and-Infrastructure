# Build with nginx image
FROM nginx:alpine

# Copy website/ to nginx html directory
COPY website/ /usr/share/nginx/html/

# Copy configuration file to nginx configuration directory
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80