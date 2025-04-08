# Dockerfile.server
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY config.ini .
COPY alarm.py .

CMD ["python", "server.py"]
