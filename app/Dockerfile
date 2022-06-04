# syntax=docker/dockerfile:1

# Set official base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Install dependencies on image
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy all files located in the current directory into the image directory
COPY . .

# Command to execute when image is executed inside a container
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]