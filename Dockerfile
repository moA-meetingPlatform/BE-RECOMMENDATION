# Use a different base image
FROM python:3.9-slim-buster

# �ʿ��� ��Ű�� ��ġ
RUN apt-get update && apt-get install -y libcurl4-openssl-dev libssl-dev build-essential

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory in the container to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ����ȯ��
ENV FLASK_ENV=development

EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "app.py"]
