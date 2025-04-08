# alarm.py
import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import socket
import configparser
import os

# Logging konfigurieren
logging.basicConfig(filename='/app/monitoring.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Lese die Konfigurationsdatei
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

# Überprüfe, ob die Datei existiert
if not os.path.exists(config_path):
    logging.error(f"Config-Datei nicht gefunden: {config_path}")
    raise FileNotFoundError(f"Config-Datei nicht gefunden: {config_path}")

config.read(config_path)

# Überprüfe, ob die Sektion [email] existiert
if 'email' not in config:
    logging.error("Sektion [email] in config.ini nicht gefunden!")
    raise KeyError("Sektion [email] in config.ini nicht gefunden!")

# E-Mail-Konfiguration aus config.ini lesen
email_config = config['email']
SMTP_SERVER = email_config['smtp_server']
SMTP_PORT = int(email_config['smtp_port'])
SENDER = email_config['sender']
RECEIVER = email_config['receiver']
SMTP_USERNAME = email_config['username']
SMTP_PASSWORD = email_config['password']
EMAIL_ALERT = email_config.get('email_alert', 'yes').lower() == 'yes'

def check_threshold(value, soft_limit, hard_limit, metric_name, hostname):
    """
    Prüft, ob ein Wert die Schwellenwerte überschreitet, loggt das Ergebnis und sendet bei Bedarf eine E-Mail.
    Args:
        value: Der gemessene Wert (z. B. 85 für disk_usage)
        soft_limit: Der Soft-Schwellenwert
        hard_limit: Der Hard-Schwellenwert
        metric_name: Name der Metrik (z. B. "disk_usage")
        hostname: Hostname des Systems
    Returns:
        String mit dem Status (z. B. "OK", "WARNING: Soft Limit exceeded", "ALERT: Hard Limit exceeded")
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"{timestamp} - {hostname} - {metric_name}: {value}"

    if value > hard_limit:
        logging.error(f"Hard Limit exceeded - {message}")
        send_email(f"ALERT: Hard Limit exceeded - {message}")
        return "ALERT: Hard Limit exceeded"
    elif value > soft_limit:
        logging.warning(f"Soft Limit exceeded - {message}")
        send_email(f"WARNING: Soft Limit exceeded - {message}")
        return "WARNING: Soft Limit exceeded"
    else:
        logging.info(message)
        return "OK"

def send_email(message):
    """
    Sendet eine E-Mail mit der angegebenen Nachricht.
    Args:
        message: Die Nachricht, die gesendet werden soll
    """
    if not EMAIL_ALERT:
        logging.info(f"E-Mail-Benachrichtigungen deaktiviert - Nachricht nicht gesendet: {message}")
        return
    msg = MIMEText(message)
    msg['Subject'] = 'Monitoring Alert'
    msg['From'] = SENDER
    msg['To'] = RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info(f"E-Mail erfolgreich gesendet: {message}")
    except Exception as e:
        logging.error(f"E-Mail-Versand fehlgeschlagen: {e}")
