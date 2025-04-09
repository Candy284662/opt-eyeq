# alarm.py
import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import socket
import configparser
import os

# Logging konfigurieren um alle Aktivitäten zu protokollieren
logging.basicConfig(filename='/app/monitoring.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Lese die Konfigurationsdatei
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

# Überprüfen, ob die Konfigurationsdatei existiert
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
SMTP_SERVER = email_config['smtp_server']  # SMTP-Server für den Versand
SMTP_PORT = int(email_config['smtp_port']) # Port für SMTP-Verbindung
SENDER = email_config['sender'] # Absender-E-Mail-Adresse
RECEIVER = email_config['receiver'] # Empfänger-E-Mail-Adresse
SMTP_USERNAME = email_config['username'] # Benutzername für SMTP-Authentifizierung
SMTP_PASSWORD = email_config['password'] # Passwort für SMTP-Authentifizierung
EMAIL_ALERT = email_config.get('email_alert', 'yes').lower() == 'yes' # E-Mail-Benachrichtigungen aktivieren/deaktivieren

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
    """ # Aktuellen Zeitstempel für die Protokollierung und Benachrichtigung erhalten
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"{timestamp} - {hostname} - {metric_name}: {value}"
# Überprüfen, ob der Wert den Hard-Limit überschreitet
    if value > hard_limit:
        logging.error(f"Hard Limit exceeded - {message}")
        send_email(f"ALERT: Hard Limit exceeded - {message}")
        return "ALERT: Hard Limit exceeded"
    elif value > soft_limit: # Überprüfen, ob der Wert den Soft-Limit überschreitet
        logging.warning(f"Soft Limit exceeded - {message}")
        send_email(f"WARNING: Soft Limit exceeded - {message}")
        return "WARNING: Soft Limit exceeded"
    else:
        logging.info(message) # Wenn der Wert im grünen Bereich liegt, logge die Info
        return "OK"

def send_email(message):
    """
    Sendet eine E-Mail mit der angegebenen Nachricht.
    Args:
        message: Die Nachricht, die gesendet werden soll
    """
    if not EMAIL_ALERT: # Wenn E-Mail-Benachrichtigungen deaktiviert sind, wird keine E-Mail gesendet
        logging.info(f"E-Mail-Benachrichtigungen deaktiviert - Nachricht nicht gesendet: {message}")
        return
    msg = MIMEText(message) # Erstelle die MIMEText-Nachricht für die E-Mail
    msg['Subject'] = 'Monitoring Alert' # Betreff der E-Mail
    msg['From'] = SENDER  # Absender-Adresse
    msg['To'] = RECEIVER  # Empfänger-Adresse

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server: # SMTP-Verbindung aufbauen, TLS verschlüsseln und die E-Mail versenden
            server.starttls() # TLS-Verschlüsselung starten
            server.login(SMTP_USERNAME, SMTP_PASSWORD) # Mit den SMTP-Anmeldedaten einloggen
            server.send_message(msg) # Nachricht senden
        logging.info(f"E-Mail erfolgreich gesendet: {message}")
    except Exception as e:  # Fehlerprotokollierung im Falle eines fehlgeschlagenen E-Mail-Versands
        logging.error(f"E-Mail-Versand fehlgeschlagen: {e}")
