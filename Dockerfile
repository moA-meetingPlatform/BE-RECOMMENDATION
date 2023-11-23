# Use an official Python runtime as a parent image
FROM python:3.9

# Install required packages
RUN apt-get update && \
  apt-get install -y ffmpeg openjdk-11-jdk && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install pip and any needed packages specified in requirements.txt
RUN apt-get update && \
  apt-get install -y python3-pip && \
  pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]