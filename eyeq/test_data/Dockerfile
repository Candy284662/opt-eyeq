FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "test_data.py"]
#Dieses Dockerfile baut ein Docker-Image, das auf Python 3.11 basiert, Abhängigkeiten
#installiert und dann das Python-Skript test_data.py ausführt, wenn der Container gestartet wird.
