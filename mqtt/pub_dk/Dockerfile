# Install python from Dockerhub
FROM python:3.7
# Set Working Directory
WORKDIR /app
ADD . /app
# Install libraries needed
RUN pip install numpy paho-mqtt
# EXPOSE PORTS for various telemetry services
EXPOSE 1883 

