# (Kinder)Impfkalender - Einträge erstellen

Python-Anwendung, die aus einem Startdatum (= Geburtsdatum) und Offsets (+ xx Monate) Kalendereinträge mit Reminder für den Import in Outlook, Thunderbird, GMAIL, etc. erstellt.

* INPUT (CSV im Arbeitsverzeichnis): Diese Infos wurden aus dem Impfkalender für Säuglinge und Kleinkinder der Stadt Wien übernommen (https://www.wien.gv.at/gesundheit/beratung-vorsorge/impfen/kalender/kleinkinder.html)
  * Impfung
  * Teilimpfung
  * Offset in Monaten
  * Infotext (wird im Kalendereintrag angezeigt)
  * Reminder (im ICAL-Format)
* OUTPUT: ICAL, PDF, CSV (werden im Download-Verzeichnis abgeleget))

Verfügbar als:
* Python Flask-Anwendung unter: https://alexontour.pythonanywhere.com/
* Google-Collab-Script

## Beispiel Import Thunderbird
![Beispiel-Import der ICS-Datei in Thunderbird](demo_import.JPG)
