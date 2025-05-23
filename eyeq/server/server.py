# Importieren der notwendigen Module
from flask import Flask, request # Flask für Webserver und HTTP-Requests
from influxdb_client import InfluxDBClient, Point # InfluxDB Client und Point für die Interaktion mit der InfluxDB
from influxdb_client.client.write_api import SYNCHRONOUS # Synchronous Schreibmodus für InfluxDB
import logging # Logging zur Protokollierung von Fehlern und Erfolgen
from datetime import datetime # Für Zeitstempel
import configparser # Zum Lesen der Konfigurationsdatei
import os  # Für die Arbeit mit Dateipfaden und Umgebungsvariablen
from alarm import check_threshold  # Import der Funktion zur Schwellenwertprüfung aus der alarm.py-Datei
app = Flask(__name__) # Initialisieren der Flask-Anwendung

# Logging konfigurieren (Log-Datei für InfluxDB-bezogene Aktivitäten)
logging.basicConfig(filename='/app/monitoring.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Konfigurationsdatei laden
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
if not os.path.exists(config_path): # Überprüfen, ob die Konfigurationsdatei existiert
    logging.error(f"Config-Datei nicht gefunden: {config_path}")
    raise FileNotFoundError(f"Config-Datei nicht gefunden: {config_path}")
# Konfigurationsdatei lesen
config.read(config_path)

# Überprüfen, ob die Sektion [influxdb] in der Konfigurationsdatei existiert
if 'influxdb' not in config:
    logging.error("Sektion [influxdb] in config.ini nicht gefunden!")
    raise KeyError("Sektion [influxdb] in config.ini nicht gefunden!")

# InfluxDB-Konfigurationswerte aus der Datei auslesen
influxdb_config = config['influxdb']
INFLUXDB_URL = influxdb_config['url']
INFLUXDB_TOKEN = influxdb_config['token']
INFLUXDB_ORG = influxdb_config['org']
BUCKET = influxdb_config['bucket']


# Initialisieren des InfluxDB-Clients
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Überprüfe, ob die Sektion [thresholds] existiert
if 'thresholds' not in config:
    logging.error("Sektion [thresholds] in config.ini nicht gefunden!")
    raise KeyError("Sektion [thresholds] in config.ini nicht gefunden!")

# Schwellenwerte aus config.ini einlesen
thresholds_config = config['thresholds']
THRESHOLDS = {
    "disk_usage": {
        "soft": int(thresholds_config['disk_soft']),
        "hard": int(thresholds_config['disk_hard'])
    },
    "memory_usage": {
        "soft": int(thresholds_config['memory_soft']),
        "hard": int(thresholds_config['memory_hard'])
    },
    "process_count": {
        "soft": int(thresholds_config['process_soft']),
        "hard": int(thresholds_config['process_hard'])
    },
    "logged_in_users": {
        "soft": int(thresholds_config.get('logged_in_users_soft', 5)),
        "hard": int(thresholds_config.get('logged_in_users_hard', 10))
    }
}

@app.route('/submit', methods=['POST']) # Definieren einer Route zum Empfangen von Systemmetriken via POST
def receive_metrics():
    data = request.json # JSON-Daten aus der POST-Anfrage extrahieren
    hostname = data.get("hostname") # Den Hostnamen aus den Daten extrahieren


    # Prüfe Schwellenwerte für jede Metrik und delegiere Alarmierung an alarm.py
    for metric, value in data.items():
        if metric in THRESHOLDS:
            soft = THRESHOLDS[metric]["soft"]
            hard = THRESHOLDS[metric]["hard"]
            # Rufe die check_threshold-Funktion aus alarm.py auf
            status = check_threshold(value, soft, hard, f"{metric} on {hostname}", hostname)

    # Schreibe die Daten in InfluxDB
    point = (
        Point("system_metrics")
        .tag("host", hostname)
        .tag("ip_address", data.get("ip_address", "unknown"))
        .tag("os", data.get("os", "unknown"))
        .field("disk_usage", float(data.get("disk_usage", 0)))
        .field("memory_usage", float(data.get("memory_usage", 0)))
        .field("process_count", float(data.get("process_count", 0)))
        .field("logged_in_users", float(data.get("logged_in_users", 0)))
        .time(datetime.utcnow().isoformat() + "Z")
    )

    try:  # Schreiben der Metriken in InfluxDB
        write_api.write(bucket=BUCKET, record=point)
        logging.info("InfluxDB Schreiben erfolgreich für POST /submit")
    except Exception as e: # Fehlerprotokollierung, falls das Schreiben fehlschlägt
        logging.error(f"InfluxDB Schreiben fehlgeschlagen: {e}")
        return {"status": "failed", "error": str(e)}, 500

    return {"status": "success"}, 200

# Starten der Flask-Anwendung
if __name__ == "__main__":  
    app.run(host="0.0.0.0", port=5000)
