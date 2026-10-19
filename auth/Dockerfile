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

# Install the Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the current directory to the project workdir
COPY . .

CMD ["gunicorn", "auth:app", "--bind", "0.0.0.0:8000"]