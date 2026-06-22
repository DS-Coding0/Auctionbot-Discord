# Architektur

## Übersicht
Das Projekt besteht aus drei Hauptteilen:
- Bot in Python mit discord.py
- Webpanel in Node.js und React
- PostgreSQL als zentrale Datenbank

## Bot
Der Bot verarbeitet:
- Discord-Interaktionen
- Live-Auktionen
- DMs
- Show-Start und Show-Ende
- Audit-Logs
- Timer und Wiederherstellung nach Neustart

## Webpanel
Das Webpanel dient Verkäufern zur Verwaltung von:
- Shows
- Artikeln
- Bildern
- Preisen
- Auktionsvorbereitung

## Datenbank
PostgreSQL speichert:
- Nutzer
- Server
- Shows
- Artikel
- Auktionen
- Gebote
- Bestellungen
- Bewertungen
- Logs

## Betriebsmodell
- Docker-Container für Bot, Webpanel und PostgreSQL
- Persistente Volumes für Daten
- Umgebungsvariablen für Konfiguration
- Healthchecks für Bot und Datenbank

## Multi-Server-Betrieb
Der Bot kann auf mehreren Discord-Servern gleichzeitig laufen. Jede Show muss einem Guild-Kontext zugeordnet sein.

## Wiederherstellung
Laufende Shows und Auktionen müssen nach einem Neustart aus der Datenbank wiederhergestellt werden.