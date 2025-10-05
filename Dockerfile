# Use an official Python runtime as a parent image
#FROM python:3.11-slim-buster
#FROM ghcr.io/browserless/chromium
# Use the official Ubuntu base image
#FROM ubuntu:latest
FROM ghcr.io/zenika/alpine-chrome

# Set environment variable to prevent interactive prompts during apt-get install
ENV DEBIAN_FRONTEND=noninteractive

USER root
RUN apk upgrade --no-cache --available \
    && apk add --no-cache \
    python3 py3-pip
USER chrome

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . .

# Copy the requirements file and install dependencies
RUN pip install --no-cache-dir -e . --break-system-packages
RUN pip install uvicorn fastapi --break-system-packages

EXPOSE 8000

# Define the command to run the application
ENTRYPOINT ["python3", "-m", "pydoll", "serve"]
