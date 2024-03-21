FROM python:3.9-slim

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

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

EXPOSE 5000

# Run the Flask application with HTTPS
CMD ["flask", "run", "--cert=cert.pem", "--key=key.pem"]
