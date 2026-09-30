# syntax=docker/dockerfile:1

# Build an image with the Python 3.14 image
FROM python:3.14-slim-trixie

# Set the working directory to `/code`
WORKDIR /code

# Install system C dependencies required by mariadb Python driver
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables used by the `flask` command
ENV FLASK_APP=auth.py
ENV FLASK_RUN_HOST=0.0.0.0

# Copy `requirements.txt`
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the current directory `.` in the project to the workdir `.` in the image
COPY . .

EXPOSE 5000

# Set the default command for the container to `flask run --debug`
CMD ["flask", "run", "--debug"]