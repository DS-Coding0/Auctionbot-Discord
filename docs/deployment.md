# Deployment

## Voraussetzungen
- Docker
- Docker Compose
- Discord-Bot-Token
- Discord OAuth2 Client-ID und Client-Secret
- PostgreSQL-Zugangsdaten

## Vorbereitung
1. `.env.example` nach `.env` kopieren.
2. Alle Tokens und Zugangsdaten eintragen.
3. Prüfen, ob die Ports 3001 und 5173 frei sind.

## Start des Systems
```bash
docker compose up --build
```

## Lokale Entwicklung
### Bot
```bash
python main.py
```

### Webpanel
```bash
cd web
npm install
npm run dev
```

## Betrieb
- PostgreSQL läuft persistent in einem Docker-Volume.
- Der Bot liest seine Konfiguration aus Umgebungsvariablen.
- Das Webpanel authentifiziert sich über Discord OAuth2.

## Backup
Backups der PostgreSQL-Datenbank sollten regelmäßig durchgeführt und extern gespeichert werden.

## Wiederherstellung
Im Fehlerfall wird die Datenbank aus einem Backup wiederhergestellt und der Bot erneut gestartet.