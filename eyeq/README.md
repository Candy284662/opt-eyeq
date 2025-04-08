# Eyeq Projekt

Dies ist das Eyeag-Projekt, das Monitoring- und Server-Funktionalitäten bereitstellt.

## Verzeichnisstruktur
- `server/`: Enthält die Server- und Monitoring-Skripte.
  - `Dockerfile`: Dockerfile zur Containerisierung der Anwendung.
  - `monitoring.py`: Skript für das Monitoring.
  - `requirements.txt`: Python-Abhängigkeiten.
  - `server.py`: Haupt-Server-Skript.

## Installation
1. Installiere Python 3 und pip.
2. Navigiere zu `server/`: `cd server`
3. Installiere Abhängigkeiten: `pip install -r requirements.txt`
4. Starte den Server: `python server.py`

## Weitere Informationen
- Protokolle werden in `server/monitoring.log` gespeichert (nicht im Repository enthalten).
- Backup-Dateien (z. B. `*.bak`) sind nicht im Repository enthalten.
