# Flask Webserver Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bluetooth \
    libbluetooth-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
