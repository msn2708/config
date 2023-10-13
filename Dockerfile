# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

VOLUME /data

EXPOSE 8421
EXPOSE 5678
# Install the required packages
RUN pip install --no-cache-dir ruamel.yaml bson flask pymongo bson ray debugpy

# Run the Python script when the container launches
CMD ["python", "get_config.py"]

HEALTHCHECK CMD curl --fail http://localhost:5000 || exit 1
