# API-Dokumentation

## Zweck
Diese Dokumentation beschreibt die interne Schnittstelle zwischen Bot, Webpanel und Datenbank.

## Hauptbereiche
- Bot-Commands für Registrierung, Shows, Auktionen, Bestellungen und Bewertungen.
- Webpanel-Endpunkte für Login, Showverwaltung und Artikelverwaltung.
- PostgreSQL als gemeinsame Datenquelle.

## Bot-seitige Operationen
- Nutzer registrieren.
- Shows anlegen, starten, verschieben und beenden.
- Artikel einer Show zuordnen.
- Auktionen starten und Gebote verarbeiten.
- Bestellungen und Bewertungen speichern.
- Audit-Logs schreiben.

## Webpanel-seitige Operationen
- Discord-Login für Verkäufer.
- Shows anlegen und verwalten.
- Artikel mit Bild, Beschreibung und Startpreis anlegen.
- Artikel einer Show zuweisen.
- Live-Status anzeigen.

## Hinweis
Die genauen HTTP-Routen werden in der Implementierung festgelegt. Das Webpanel darf keine eigene Auktionslogik parallel zum Bot besitzen.