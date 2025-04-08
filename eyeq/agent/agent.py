#!/usr/bin/env python3
# server-agent.py (für lokale Ausführung auf dem Host)
import psutil
import socket
import platform
import requests
import time
import logging

# Logging konfigurieren
logging.basicConfig(
    filename='agent.log',  # Log-Datei im aktuellen Verzeichnis
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Funktion zum Ermitteln der IP-Adresse
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 80))  # Verbindung zu Google DNS, um die IP zu ermitteln
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        logging.error(f"Fehler beim Ermitteln der IP-Adresse: {e}")
        return "unknown"

# Metriken sammeln
def get_disk_usage():
    return psutil.disk_usage('/').percent  # Direkt auf das Host-Dateisystem zugreifen

def get_memory_usage():
    return psutil.virtual_memory().percent

def get_process_count():
    return len(psutil.pids())

def get_logged_in_users():
    users = psutil.users()
    return len(users)

def collect_metrics():
    hostname = socket.gethostname()
    ip_address = get_ip_address()
    os_info = f"{platform.system()} {platform.release()}"

    metrics = {
        "hostname": hostname,
        "ip_address": ip_address,
        "os": os_info,
        "disk_usage": get_disk_usage(),
        "memory_usage": get_memory_usage(),
        "process_count": get_process_count(),
        "logged_in_users": get_logged_in_users()
    }
    return metrics

# Metriken an den Server senden
def send_to_server(metrics):
    try:
        # Der Server läuft in Docker, daher verwenden wir den Service-Namen
        response = requests.post("http://localhost:5000/submit", json=metrics)
        if response.status_code == 200:
            logging.info("Daten erfolgreich an Server gesendet")
        else:
            logging.error(f"Fehler beim Senden der Daten: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Fehler beim Senden der Daten an den Server: {e}")

# Hauptloop des Agenten
def agent_loop():
    logging.info("Starte Agent lokal auf dem Host...")
    while True:
        try:
            metrics = collect_metrics()
            logging.info(f"Erfasste Metriken: {metrics}")
            send_to_server(metrics)
        except Exception as e:
            logging.error(f"Fehler im Agent-Loop: {e}")
        time.sleep(60)  # Sende alle 60 Sekunden

if __name__ == "__main__":
    agent_loop()
