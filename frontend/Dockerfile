# Build with nginx image
FROM nginx:alpine

# Copy website/ to nginx html directory
COPY website/ /usr/share/nginx/html/

# Remove default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy configuration template
COPY default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80