# Use a different base image
FROM python:3.9-slim-buster

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y libcurl4-openssl-dev libssl-dev build-essential

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory in the container to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 개발환경
ENV FLASK_ENV=development

# Run app.py when the container launches
CMD ["python", "app.py"]
