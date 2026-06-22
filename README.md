# Auction Bot Project

Dieses Projekt ist eine Discord-basierte Live-Auktionsplattform mit Python-Bot, PostgreSQL, Docker und einem separaten Webpanel für Verkäufer.

## Bestandteile
- **bot**: Discord-Bot für Auktionen, Shows, Gebote, DMs und Audit-Logs.
- **db**: PostgreSQL-Datenmodell und Datenzugriff.
- **web**: Node.js + React Webpanel für Verkäufer.
- **deploy**: Dockerfiles für Bot und Webpanel.
- **scripts**: Datenbank-Init, Backup und Restore.
- **docs**: Pflichtenheft und Architektur-Dokumentation.

## Voraussetzungen
- Docker und Docker Compose
- Python 3.12 für lokale Entwicklung
- Node.js 20 für das Webpanel

## Einrichtung
1. `.env.example` nach `.env` kopieren.
2. Discord Token, Client-ID, Client-Secret und PostgreSQL-Zugangsdaten eintragen.
3. `docker compose up --build` ausführen.

## Start
### Komplettes System
```bash
docker compose up --build
```

### Nur Bot lokal
```bash
python main.py
```

### Webpanel lokal
```bash
cd web
npm install
npm run dev
```

## Struktur
Die genaue Projektstruktur findest du in `PROJECT_STRUCTURE.txt`.

## Nächste Schritte
- Slash Commands implementieren
- DB-Repositories ausbauen
- Show-, Artikel- und Auktionslogik ergänzen
- Webpanel-Login und Formularlogik fertigstellen