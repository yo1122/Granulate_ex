FROM python:3.9-slim

ENV FLASK_APP=app.py

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssl \
        && \
    rm -rf /var/lib/apt/lists/*

# Handle files
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate SSL/TLS certificates
RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=IT/CN=localhost"

# Set default values for host and port
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=5000

EXPOSE $SERVER_PORT

# Run the Flask application with HTTPS
CMD ["sh", "-c", "flask run --cert=cert.pem --key=key.pem --port=$SERVER_PORT --host=$SERVER_HOST"]
