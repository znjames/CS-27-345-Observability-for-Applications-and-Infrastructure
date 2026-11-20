# Build with the official nginx Alpine image containing the native OTel module.
FROM nginx:mainline-alpine-otel

# Copy website/ to nginx html directory
COPY website/ /usr/share/nginx/html/

# Remove default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy configuration template
COPY default.conf.template /etc/nginx/templates/default.conf.template

# Load the native OTel dynamic module in the main nginx context.
RUN sed -i '1i load_module /usr/lib/nginx/modules/ngx_otel_module.so;' /etc/nginx/nginx.conf

EXPOSE 80