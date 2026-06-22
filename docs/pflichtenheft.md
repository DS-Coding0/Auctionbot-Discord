# Pflichtenheft
## Live-Auktions-Bot für Discord in Python
## Version 1.3

### 1. Zielsetzung
1.1 Der Bot soll Live-Auktionen in Discord ermöglichen, bei denen registrierte Nutzer Artikel einstellen, ansehen und per Button bieten können.
1.2 Der Bot muss Auktionen mit Startpreis, Zeitlimit, Maximalgebot und automatischer Preissteigerung abbilden.
1.3 Der Bot soll Einzelauktionen und Massenauktionen unterstützen.
1.4 Zusätzlich sollen mehrere Käufe zu einer Bestellung gebündelt werden, solange diese noch nicht als versendet markiert ist.
1.5 Für abgeschlossene Bestellungen soll ein 5-Sterne-Bewertungssystem integriert werden.
1.6 Verkäufer sollen ihre Shows und Artikel zusätzlich über ein Webpanel verwalten können.

### 2. Ausgangssituation
2.1 Es besteht der Wunsch, Auktionen direkt in Discord durchzuführen.
2.2 Artikel werden vorab angelegt, Nutzer müssen sich per Discord-ID registrieren, und das Bieten soll im Live-Betrieb möglichst einfach und fair ablaufen.
2.3 Der Bot soll später erweiterbar sein.
2.4 Zusätzlich sollen Auktionen in thematische Shows eingebettet werden, die zeitlich geplant und einem Discord-Sprachkanal mit Live-Übertragung zugeordnet sind.
2.5 Verkäufer sollen ein Webpanel nutzen können, um Shows und Artikel komfortabel anzulegen und zu verwalten.

### 3. Systembeschreibung
3.1 Der Bot ist ein Discord-Application-Bot in Python.
3.2 Er nutzt Slash Commands, Buttons, Embeds und Datenbankpersistenz.
3.3 Die operative Logik liegt auf einem oder mehreren Discord-Servern in definierten Kanälen, z. B. einem Auktionskanal, einem Live-Kanal und einem Admin-Logkanal.
3.4 Der Bot muss mehrere Server parallel unterstützen können.
3.5 Zusätzlich gibt es ein Webpanel in Node.js und React für Verkäufer und Administratoren.
3.6 Webpanel, Bot und Datenbank greifen auf dieselbe PostgreSQL-Datenbasis zu.

### 4. Beteiligte Rollen
4.1 Administrator: verwaltet Nutzer, Artikel, Auktionen und Systemeinstellungen.
4.2 Auktionator: startet Auktionen und kann sie moderieren.
4.3 Registrierter Bieter: darf bieten und ein Maximalgebot hinterlegen.
4.4 Registrierter Verkäufer/Inserent: darf Artikel anlegen und Shows verwalten.
4.5 Unregistrierter Nutzer: kann Auktionen ansehen, aber nicht interagieren.
4.6 Käufer: erhält Bestellungen und kann abgeschlossene Bestellungen bewerten.
4.7 Server-Admin: verwaltet nur Inhalte auf seinem Discord-Server, sofern der Bot auf mehreren Servern aktiv ist.

### 5. Muss-Anforderungen
#### 5.1 Registrierung
5.1.1 Nutzer müssen sich vor dem Bieten und Inserieren registrieren.
5.1.2 Registrierung erfolgt über die Discord-ID und muss serverübergreifend eindeutig speicherbar sein.
5.1.3 Eine Discord-ID darf nur einmal registriert werden.
5.1.4 Der Registrierungsstatus muss dauerhaft gespeichert werden.

#### 5.2 Artikelverwaltung
5.2.1 Artikel müssen vorab angelegt werden können.
5.2.2 Jeder Artikel benötigt mindestens Titel, Beschreibung und Startpreis.
5.2.3 Optional können Bild, Sofortkaufpreis, Mindestschritt und Reservierungspreis angegeben werden.
5.2.4 Artikel sollen Kategorien wie Einzelkarten, Slabs und Sealed zugeordnet werden können.
5.2.5 Artikel müssen bearbeitet, deaktiviert und gelöscht werden können.

#### 5.3 Auktionsstart
5.3.1 Auktionen können aus einem vorher angelegten Artikel gestartet werden.
5.3.2 Es muss eine Massenfunktion geben, um mehrere nummerierte Auktionen nacheinander zu starten.
5.3.3 Beim Start muss der Auktionsstatus auf „laufend“ gesetzt werden.
5.3.4 Jede Auktion soll einer bestimmten Show zugeordnet werden können.
5.3.5 Angelegte Artikel müssen vor dem Start einer Show einer Show zugewiesen werden.
5.3.6 Jede Show muss einem konkreten Discord-Server zugeordnet werden.
5.3.7 Die Auktion muss in einem definierbaren Discord-Kanal angezeigt werden.

#### 5.4 Bietfunktion
5.4.1 Bieten muss über einen Discord-Button möglich sein.
5.4.2 Pro Klick wird der Preis um 1 Euro erhöht.
5.4.3 Registrierte Nutzer können ein Maximalgebot setzen.
5.4.4 Das Maximalgebot darf nur dem jeweiligen Nutzer angezeigt werden.
5.4.5 Der Bot muss automatisch bis zum Maximalgebot mitbieten.

#### 5.5 Timer und Auktionende
5.5.1 Jede Auktion muss eine definierte Laufzeit haben.
5.5.2 Bei einem neuen Gebot soll der Timer bei Bedarf auf einen definierten Wert zurückgesetzt werden, sofern die Restzeit unterhalb des Schwellenwerts liegt.
5.5.3 Nach Ablauf der Zeit ohne neues Gebot muss die Auktion automatisch enden.
5.5.4 Der Gewinner und der Endpreis müssen gespeichert werden.

#### 5.6 Protokollierung
5.6.1 Alle Gebote müssen protokolliert werden.
5.6.2 Alle administrativen Aktionen müssen protokolliert werden.
5.6.3 Fehler, Abbrüche und automatische Enden müssen im Logkanal oder in der Datenbank nachvollziehbar sein.

#### 5.7 Neustart- und Persistenzsicherheit
5.7.1 Laufende Auktionen dürfen bei einem Bot-Neustart nicht verloren gehen.
5.7.2 Persistente Buttons und Statusdaten müssen nach dem Start wiederhergestellt werden.
5.7.3 Die Datenbank muss als führende Quelle für den aktuellen Zustand dienen.
5.7.4 Mehrere Shows müssen parallel verwaltbar sein, ohne dass Timer oder Zustände kollidieren.

#### 5.8 Bestellungen
5.8.1 Mehrere Käufe eines Nutzers sollen als eine Bestellung gebündelt werden, solange die Bestellung noch nicht als versendet markiert wurde.
5.8.2 Eine Bestellung kann mehrere Artikel enthalten.
5.8.3 Der Verkäufer muss Bestellungen als versendet markieren können.
5.8.4 Nach dem Versand ist eine weitere Bündelung zusätzlicher Käufe in dieselbe Bestellung nicht mehr möglich.

#### 5.9 Bewertungssystem
5.9.1 Für jede abgeschlossene Bestellung soll eine 5-Sterne-Bewertung vergeben werden können.
5.9.2 Bewertungen dürfen nur nach Abschluss der Bestellung möglich sein.
5.9.3 Jede Bestellung darf nur einmal bewertet werden oder muss klar definierte Mehrfachbewertungsregeln erhalten.
5.9.4 Bewertungen müssen dauerhaft gespeichert werden.

### 6. Soll-Anforderungen
6.1 Sofortkauf-Funktion als optionale Funktion.
6.2 Kein Reservierungspreis vorgesehen.
6.3 Benachrichtigung bei Überbotenwerden.
6.4 Private Anzeige des Maximalgebots für den Bieter.
6.5 Erinnerungen kurz vor Auktionsende.
6.6 Export von Auktionsdaten als CSV oder JSON.
6.7 Admin-Funktion zum Pausieren und Fortsetzen von Auktionen.
6.8 Bewertungsübersicht pro Verkäufer oder pro Artikel, öffentlich sichtbar.
6.9 Filter für offene, versendete und bewertete Bestellungen.
6.10 Jede Auktion kann optional mit einem Foto versehen werden.
6.11 Shows können mit Datum, Uhrzeit und Namen angelegt werden.
6.12 Auktionen können über einen Discord-Sprachkanal mit Live-Übertragung verknüpft werden.
6.13 Registrierte Nutzer können Shows vormerken.
6.14 Vorgemerkte Nutzer erhalten kurz vor Start der Show eine DM-Erinnerung.
6.15 Verkäufer können Shows starten und beenden.
6.16 Beim Beenden einer Show werden automatische DMs mit Bestellübersichten an Käufer und Verkäufer versendet.
6.17 Show-Daten wie Datum und Uhrzeit können vom Verkäufer verschoben werden.
6.18 Vorgemerkte Nutzer werden über Show-Verschiebungen informiert.

### 7. Kann-Anforderungen
7.1 Web-Dashboard für Administration.
7.2 Bildgalerie pro Artikel.
7.3 Kategorien und Filter für Artikel.
7.4 Sprachkanal-Unterstützung für Live-Auktionen.
7.5 Automatische Rechnungs- oder Gewinnerbenachrichtigung.
7.6 Statistiken zu Bewertungen, Bestellungen und Umsätzen.

### 8. Benutzeroberflächen
#### 8.1 Discord-Commands
8.1.1 `/register`
8.1.2 `/item add`
8.1.3 `/item edit`
8.1.4 `/item list`
8.1.5 `/auction start`
8.1.6 `/auction stop`
8.1.7 `/auction pause`
8.1.8 `/auction resume`
8.1.9 `/auction list`
8.1.10 `/bid max`
8.1.11 `/order list`
8.1.12 `/order ship`
8.1.13 `/rating give`
8.1.14 `/show add`
8.1.15 `/show list`

#### 8.2 Live-Auktionsansicht
8.2.1 Artikelname.
8.2.2 Beschreibung.
8.2.3 Bild.
8.2.4 Aktueller Preis.
8.2.5 Startpreis.
8.2.6 Restzeit.
8.2.7 Bieten-Button.
8.2.8 Optional Sofortkauf-Button.

#### 8.3 Bestellansicht
8.3.1 Bestellnummer.
8.3.2 Enthaltene Artikel.
8.3.3 Gesamtpreis.
8.3.4 Versandstatus.
8.3.5 Bewertungsstatus.
8.3.6 Bewertungsabgabe mit 1 bis 5 Sternen.

#### 8.4 Webpanel
8.4.1 Verkäufer melden sich über Discord OAuth2 an.
8.4.2 Verkäufer sehen ein Dashboard mit ihren Shows, Artikeln und laufenden Auktionen.
8.4.3 Verkäufer können Shows mit Name, Datum, Uhrzeit und Serverzuordnung anlegen.
8.4.4 Verkäufer können Shows verschieben, starten und beenden.
8.4.5 Verkäufer können für jede Show Artikel anlegen, bearbeiten und mit Kategorien versehen.
8.4.6 Verkäufer können Artikel mit Beschreibung, Foto, Startpreis, optionalem Sofortkaufpreis und weiteren Auktionsparametern erfassen.
8.4.7 Verkäufer können Artikel einer Show zuordnen.
8.4.8 Das Webpanel zeigt Statusinformationen, vorbereitete Auktionen und relevante Logs an.
8.4.9 Das Webpanel arbeitet ausschließlich gegen dieselbe PostgreSQL-Datenbank wie der Bot.
8.4.10 Das Webpanel darf keine eigene Auktionslogik parallel zur Bot-Logik implementieren.

### 9. Fachliche Regeln
9.1 Unregistrierte Nutzer dürfen nicht bieten.
9.2 Ein Gebot muss immer den aktuellen Preis erhöhen.
9.3 Das Maximalgebot darf nie öffentlich angezeigt werden.
9.4 Bei gleichem Gebot entscheidet die Serverlogik deterministisch.
9.5 Auktionen dürfen nur mit gültigen Artikeldaten gestartet werden.
9.6 Endpreise werden in ganzen Eurobeträgen geführt.
9.7 Offene Käufe werden automatisch zu einer gemeinsamen Bestellung gebündelt.
9.8 Eine Bestellung gilt nur dann als abgeschlossen im Bewertungssinn, wenn sie geliefert oder als abgeschlossen markiert wurde.
9.9 Jede Bestellung darf nur gemäß der definierten Bewertungsregel bewertet werden.

### 10. Datenhaltung
10.1 Die Anwendung benötigt mindestens folgende Datenobjekte:
10.1.1 Nutzerstammdaten.
10.1.2 Serverstammdaten.
10.1.3 Artikelstammdaten.
10.1.4 Showdaten.
10.1.5 Auktionsdaten.
10.1.6 Gebotsdaten.
10.1.7 Bestelldaten.
10.1.8 Bewertungsdaten.
10.1.9 Logdaten.
10.1.10 Konfigurationsdaten.

10.2 Die Anwendung soll direkt auf PostgreSQL laufen.
10.3 SQLite ist nicht als Zielsystem vorgesehen.
10.4 Die Datenbankanbindung muss auf den produktiven PostgreSQL-Betrieb ausgelegt sein.

### 11. Nicht-funktionale Anforderungen
11.1 Zuverlässigkeit: Auktionsstatus muss auch bei Abstürzen korrekt wiederhergestellt werden.
11.2 Sicherheit: Tokens und sensible Konfigurationsdaten dürfen nicht im Code stehen.
11.3 Performanz: Gebotsaktionen müssen schnell verarbeitet werden.
11.4 Wartbarkeit: Die Codebasis soll modular aufgebaut sein.
11.5 Erweiterbarkeit: Neue Auktionsformen sollen später ergänzt werden können.
11.6 Nachvollziehbarkeit: Alle Änderungen am Auktionstatus müssen dokumentiert werden.
11.7 Datenkonsistenz: Bestellungen und Bewertungen müssen widerspruchsfrei gespeichert werden.
11.8 Auditierbarkeit: Kritische Vorgänge müssen im Audit-Log vollständig nachvollziehbar sein.
11.9 Robustheit: Abbrüche müssen über Rollback-Logik ohne Datenverlust behandelbar sein.
11.10 Skalierbarkeit: Der Bot muss mehrere Discord-Server gleichzeitig bedienen können.
11.11 Parallelität: Mehrere Shows können gleichzeitig laufen, ohne sich gegenseitig zu blockieren.
11.12 Usability: Das Webpanel muss eine einfache und klare Bedienung für Verkäufer bieten.

### 12. Technische Randbedingungen
12.1 Programmiersprache: Python.
12.2 Bot-Bibliothek: discord.py.
12.3 Datenbank: PostgreSQL.
12.4 Architektur: modular mit getrennten Bereichen für Commands, Views, Logik und Datenbank.
12.5 Zusätzlich wird das Projekt in Bot, Webpanel und Datenbank-Teilbereiche getrennt.
12.6 Das Webpanel wird in Node.js und React umgesetzt.
12.7 Hosting: kompletter Docker-Container bzw. Docker-Compose-basierte Umgebung.
12.8 Der gesamte Bot soll containerisiert ausgeliefert werden.

### 13. Betriebsbedingungen
13.1 Der Bot kann auf mehreren Discord-Servern gleichzeitig laufen.
13.2 Es muss ein Admin-Team geben, das Auktionen und Bestellungen überwacht.
13.3 Die Uhrzeit und Laufzeiten müssen serverseitig berechnet werden.
13.4 Bei Bot-Neustart muss ein Wiederanlaufmechanismus greifen.
13.5 Shows sollen an einen Sprachkanal und den jeweiligen Live-Übertragungs-Workflow gebunden werden können.
13.6 Beim Verschieben einer Show müssen alle vorgemerkten Nutzer automatisch informiert werden.
13.7 Kritische Änderungen müssen im Audit-Log erfasst werden.
13.8 Pro Show muss der zugehörige Discord-Server gespeichert werden.
13.9 Mehrere Shows müssen parallel auf verschiedenen Servern verwaltet werden können.
13.10 Das Webpanel muss parallel zum Bot auf dieselbe PostgreSQL-Datenbasis zugreifen können.

### 14. Risiken und Gegenmaßnahmen
14.1 Doppelte Gebote durch Klickspamming: durch Sperrlogik und atomare Datenbanktransaktionen absichern.
14.2 Bot-Neustarts während laufender Auktionen: persistente Speicherung und Wiederherstellung einsetzen.
14.3 Streit über Gebotsreihenfolge: vollständige Gebotshistorie protokollieren.
14.4 Falsche Bestellzusammenführung: offene Bestellungen strikt prüfen und automatisch nur bis zur letzten noch nicht versendeten Bestellung bündeln.
14.5 Unfaire Bewertungen: Bewertungen nur nach Abschluss und mit eindeutiger Referenz zur Bestellung erlauben.
14.6 Abbrüche während Shows oder Auktionen: Rollback-Mechanismen müssen den letzten konsistenten Zustand wiederherstellen.
14.7 Inkonsistenzen zwischen Webpanel und Bot: beide Systeme müssen dieselben DB-Services und Statusregeln verwenden.

### 15. Abnahmekriterien
15.1 Ein Nutzer kann sich per Discord-ID registrieren.
15.2 Ein registrierter Nutzer kann einen Artikel anlegen.
15.3 Ein Admin kann eine Auktion starten.
15.4 Ein Bieter kann per Button bieten.
15.5 Ein Maximalgebot wird korrekt verarbeitet, ohne öffentlich sichtbar zu sein.
15.6 Der Timer wird bei Bedarf nach Regelwerk zurückgesetzt.
15.7 Die Auktion endet automatisch und speichert Gewinner und Endpreis.
15.8 Mehrere Käufe werden zu einer offenen Bestellung zusammengefasst, solange sie noch nicht als versendet markiert wurde.
15.9 Ein Verkäufer kann eine Bestellung als versendet markieren.
15.10 Für eine abgeschlossene Bestellung kann eine 5-Sterne-Bewertung vergeben und gespeichert werden.
15.11 Eine Show kann mit Datum, Uhrzeit und Name angelegt werden.
15.12 Artikel können Kategorien zugeordnet werden.
15.13 Eine Auktion kann einer bestimmten Show zugeordnet werden.
15.14 Zu einer Auktion kann optional ein Foto hinzugefügt werden.
15.15 Der Bot funktioniert nach Neustart mit laufenden Auktionen weiter.
15.16 Beim Beenden einer Show erhalten Käufer und Verkäufer korrekte DM-Zusammenfassungen.
15.17 Eine Show kann vom Verkäufer gestartet und beendet werden.
15.18 Artikel müssen vor der Auktion einer Show zugeordnet sein.
15.19 Eine verschobene Show löst Benachrichtigungen an vorgemerkte Nutzer aus.
15.20 Kritische Änderungen erscheinen vollständig im Audit-Log.
15.21 Abbrüche während Shows oder Auktionen werden ohne Inkonsistenzen zurückgerollt.
15.22 Der Bot speichert den zugehörigen Discord-Server je Show.
15.23 Mehrere Shows können gleichzeitig auf verschiedenen Servern laufen.
15.24 Verkäufer können sich im Webpanel per Discord einloggen.
15.25 Verkäufer können im Webpanel Shows anlegen, verschieben, starten und beenden.
15.26 Verkäufer können im Webpanel Artikel mit Beschreibung, Foto und Auktionsparametern anlegen.
15.27 Das Webpanel und der Bot arbeiten konsistent auf derselben PostgreSQL-Datenbank.

### 16. Offene Punkte
16.1 Soll Sofortkauf verpflichtend oder optional sein? Optional.
16.2 Wie hoch ist der Standard-Mindestschritt je Preisbereich? Pro Gebot 1 Euro.
16.3 Soll es pro Artikel eine Reservierung geben? Nein, keine Reservierungen.
16.4 Soll der Bot Bieter bei Überbotung per DM informieren? Nein.
16.5 Sollen Auktionen im Kanal oder ausschließlich per Embed ablaufen? Embed ist vorgesehen.
16.6 Braucht es einen Webzugang für Admins? Nein, aktuell nicht.
16.7 Soll die Bewertung nur für Käufer, nur für Verkäufer oder gegenseitig möglich sein? Gegenseitig.
16.8 Soll die Bewertungsanzeige öffentlich oder nur intern sein? Öffentlich.
16.9 Wie soll die Live-Übertragung technisch mit dem Sprachkanal umgesetzt werden? Über eine unterstützende Videoübertragung im Sprachkanal.
16.10 Soll pro Show eine feste Reihenfolge der Auktionen erzwungen werden? Nein, der Verkäufer bestimmt die Startreihenfolge der Auktionen.

### 17. Empfohlene Projektphasen
17.1 Datenmodell und PostgreSQL-Schema aufsetzen.
17.2 Registrierung und Rollenprüfung umsetzen.
17.3 Artikelverwaltung bauen.
17.4 Auktionsstart und Live-Ansicht erstellen.
17.5 Bieten, Maximalgebot und Timerlogik implementieren.
17.6 Bestellungen und Bewertungssystem ergänzen.
17.7 Logging, Wiederherstellung, Fehlerbehandlung, Systemaufteilung und Dockerisierung ergänzen.
17.8 Webpanel mit Discord-OAuth, Showverwaltung und Artikelverwaltung umsetzen.
17.9 Tests, Feinschliff und produktiven Rollout durchführen.

### 18. Ergebnis
18.1 Das System bildet eine vollständige Discord-basierte Auktionsplattform mit Registrierung, Artikelverwaltung, Live-Bietfunktion, Bestellbündelung, Bewertungsfunktion und robuster Persistenz.
18.2 Die Lösung ist auf Erweiterbarkeit und langfristigen Betrieb ausgelegt.

### 19. Weitere sinnvolle Ergänzungen
19.1 Einrollen und Zurückrollen von Shows oder Auktionen bei Fehlern oder Abbrüchen.
19.2 Wartelisten- oder Nachrückerfunktion für ausverkaufte oder bereits gestartete Shows.
19.3 Rollen- oder Berechtigungssystem für Verkäufer, Auktionatoren und Moderatoren.
19.4 Automatische Rechnungs- oder Belegfunktion für abgeschlossene Bestellungen.
19.5 Sammelversand soll automatisch erfolgen, solange der letzte Kauf noch nicht als versendet markiert ist.
19.6 Export von Show-, Auktions- und Bestelldaten für Buchhaltung oder Analyse.
19.7 Datenschutz- und Löschkonzept für Nutzer-, Bestell- und Bewertungsdaten.
19.8 Rate-Limits und Missbrauchsschutz für Buttons, Commands und DMs.
19.9 Audit-Log für kritische Änderungen wie Show-Verschiebung, Show-Ende, Bewertungsänderungen, Auktionserstellungen und Fehlerfälle.
19.10 Fehler- und Rollback-Logik für Shows und Auktionen bei Abbrüchen muss fest integriert sein.
19.11 Benachrichtigungen für das Erreichen von Mindestverkaufswerten oder Reservierungspreisen.
19.12 Mehrsprachigkeit oder zumindest klare Sprachtrennung für Käuferkommunikation und Admin-Kommunikation.

### 20. Containerisierung
20.1 Das gesamte System soll als kompletter Docker-Container betrieben werden.
20.2 Für die Auslieferung soll eine Docker-Compose-Umgebung vorgesehen werden, falls Bot und PostgreSQL getrennt gestartet werden.
20.3 Konfigurationen wie Token, Datenbank-URL und Kanal-IDs müssen über Umgebungsvariablen oder Secrets injiziert werden.
20.4 Persistente Daten müssen über Docker-Volumes gesichert werden.
20.5 Der Bot muss nach Container-Neustarts seinen Zustand aus PostgreSQL wiederherstellen.

### 21. Architektur von PostgreSQL und Docker
21.1 PostgreSQL speichert alle persistierten Fachdaten wie Nutzer, Artikel, Shows, Auktionen, Gebote, Bestellungen, Bewertungen und Audit-Logs.
21.2 Der Bot läuft in einem Docker-Container und verbindet sich über eine Konfigurations-URL mit PostgreSQL.
21.3 Die Docker-Umgebung muss reproduzierbar sein und beim Neustart den kompletten Systemzustand aus der Datenbank wiederherstellen.
21.4 Sensible Daten wie Bot-Token und DB-Zugangsdaten dürfen nur über Umgebungsvariablen oder Secrets bereitgestellt werden.
21.5 Persistente Volumes müssen für PostgreSQL und gegebenenfalls Exportdaten vorgesehen werden.
21.6 Ein separates Healthcheck-Konzept soll sicherstellen, dass Bot und Datenbank korrekt starten.
21.7 Die Containerisierung muss so aufgebaut sein, dass spätere Erweiterungen ohne Bruch möglich sind.

### 22. Projektstruktur und Systemaufteilung
22.1 Das Gesamtprojekt wird in drei Hauptbereiche aufgeteilt: Bot, Webpanel und Datenbank.
22.2 Der Bot übernimmt Discord-Interaktionen, Live-Auktionen, Show-Logik, Audit-Logging und DM-Benachrichtigungen.
22.3 Das Webpanel übernimmt die Verkäuferverwaltung über Discord-Login, das Anlegen von Shows und das Erfassen von Artikeln mit Bild, Beschreibung und Auktionsparametern.
22.4 Die Datenbank speichert alle persistierten Daten für Bot und Webpanel zentral in PostgreSQL.
22.5 Bot und Webpanel müssen dieselbe Datenbasis verwenden, damit Shows, Artikel, Auktionen und Bewertungen konsistent bleiben.
22.6 Mehrere Discord-Server werden über die Guild-ID in den Show- und Auktionsdaten getrennt verwaltet.
22.7 Mehrere Shows können gleichzeitig aktiv sein, auch auf unterschiedlichen Servern.
22.8 Die Projektstruktur soll klar zwischen API-, UI-, Bot- und Datenbanklogik trennen.

### 23. Empfohlene Verzeichnisstruktur
23.1 `/bot` für Discord-Bot-Logik, Cogs, Views und Services.
23.2 `/db` für SQLAlchemy-Modelle, Session-Handling, Migrationen und SQL-Schema.
23.3 `/web` für das React-Frontend, Node.js-Backend und Discord-OAuth.
23.4 `/scripts` für Initialisierung, Backups und Hilfsskripte.
23.5 `/deploy` für Docker- und Compose-Dateien sowie Umgebungsbeispiele.
23.6 `/docs` für Spezifikation, Betriebsanleitungen und technische Dokumentation.

### 24. Verantwortlichkeiten der Komponenten
24.1 Der Bot verarbeitet alle zeitkritischen Vorgänge wie Gebote, Show-Start, Show-Ende und DM-Benachrichtigungen.
24.2 Das Webpanel stellt die Bedienoberfläche für Verkäufer bereit, insbesondere für Show- und Artikelverwaltung.
24.3 Die Datenbank ist die einzige Quelle für persistente Zustände und historische Daten.
24.4 Das Audit-Log wird zentral in PostgreSQL gespeichert und von Bot sowie Webpanel beschrieben.
24.5 Die Show-Zuordnung und der Serverbezug werden in der Datenbank gepflegt, nicht im UI allein.

### 25. Schnittstellen zwischen Bot und Webpanel
25.1 Das Webpanel legt Shows und Artikel in PostgreSQL an.
25.2 Der Bot liest diese Einträge aus PostgreSQL und startet daraus Auktionen.
25.3 Der Bot schreibt Live-Zustände wie Gebote, Auktionen, Abschluss und Audit-Events zurück in PostgreSQL.
25.4 Das Webpanel kann den Status von Shows und Artikeln anzeigen, darf jedoch keine Auktionslogik doppelt implementieren.
25.5 Discord-OAuth dient ausschließlich der Identifikation und Autorisierung der Verkäufer.