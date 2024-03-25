# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV SERVER_HOST=localhost \
    SERVER_PORT=5000 \
    MESSAGE_DB_NAME=mydatabase \
    MESSAGE_DB_HOST=dbhost \
    MESSAGE_DB_PORT=5432 \
    MESSAGE_DB_USER=dbuser \
    MESSAGE_DB_PASS=dbpassword \
    SECRET_KEY=mysecretkey \
    CERT_PATH=/path/to/cert.crt \
    KEY_PATH=/path/to/key.key

# Set working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Run the client
CMD ["python", "client.py"]
