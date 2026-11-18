# Build from gunicorn base image
FROM ghcr.io/benoitc/gunicorn:24.1.0

# Set the working directory to /code
WORKDIR /code

# Install system C dependencies required by mariadb Python driver
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
USER gunicorn

# Include gunicorn bin in the PATH
ENV PATH="/home/gunicorn/.local/bin:${PATH}"

# Install the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Install zero code instrumentation version of requirements
RUN opentelemetry-bootstrap -a install

# Copy the current directory to the project workdir
COPY . .

CMD ["opentelemetry-instrument", \
    "--traces_exporter", "otlp", \
    "--metrics_exporter", "otlp", \
    "--logs_exporter", "otlp", \
    "--service_name", "banking", \
    "gunicorn", "banking:app", "--bind", "0.0.0.0:8000"]