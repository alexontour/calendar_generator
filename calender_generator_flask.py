#!/usr/bin/env python
# coding: utf-8

# In[1]:


#pip install flask icalendar ics reportlab fpdf pdfkit pandas matplotlib wkhtmltopdf


# In[2]:


from datetime import datetime, timedelta
import pandas as pd
from fpdf import FPDF
import uuid
import csv
#from icalendar import Calendar, Event
#from datetime import datetime
import os
from flask import Flask, render_template, request, send_file


# In[3]:


def kalenderwochen_start_end_datum(eingabedatum, wochen_zukunft):
    # Konvertiere das Eingabedatum in ein datetime-Objekt
    eingabedatum_obj = datetime.strptime(eingabedatum, "%Y-%m-%d")
    print(eingabedatum)

    # Berechne das Enddatum
    enddatum = eingabedatum_obj + timedelta(weeks=wochen_zukunft)

    # Finde den Montag der Kalenderwoche des Eingabedatums
    montag_kw_start = eingabedatum_obj - timedelta(days=eingabedatum_obj.weekday())

    # Berechne das Startdatum der Kalenderwoche
    startdatum_kw = montag_kw_start + timedelta(weeks=wochen_zukunft)

    # Finde den Sonntag der Kalenderwoche
    sonntag_kw_end = montag_kw_start + timedelta(days=6) + timedelta(weeks=wochen_zukunft)

    return startdatum_kw.strftime("%Y%m%d"), sonntag_kw_end.strftime("%Y%m%d")


# In[4]:


def create_ics_from_dataframe(df, ics_filename):
    with open(ics_filename, 'w') as f:
        f.write("BEGIN:VCALENDAR\n")
        f.write("VERSION:2.0\n")
        f.write("PRODID:alexontour\n")

        for index, row in df.iterrows():
            f.write("BEGIN:VEVENT\n")
            f.write(f"UID:{uuid.uuid4()}\n")
            f.write(f"SUMMARY:{row['beschreibung']}\n")
            f.write(f"DTSTART;VALUE=DATE:{row['start'].split('.')[0]}\n")
            f.write(f"DTEND;VALUE=DATE:{row['end'].split('.')[0]}\n")
            f.write("TRANSP:TRANSPARENT\n")  # Ganztagesereignis
            f.write(f"DESCRIPTION:{row['info']}\n")
            f.write("BEGIN:VALARM\n")
            f.write("ACTION:DISPLAY\n")
            f.write(f"DESCRIPTION:Reminder - {row['beschreibung']}\n")
            f.write(f"TRIGGER:{row['reminder']}\n")  # Erinnerung
            f.write("END:VALARM\n")
            f.write("END:VEVENT\n")

        f.write("END:VCALENDAR\n")


    print(f"ICS wurde erfolgreich erstellt: {ics_filename}")


# In[5]:


def create_pdf_from_dataframe(df, pdf_filename):
    pdf = FPDF()
    # Erstellen Sie ein PDF-Objekt mit Querformat
    #pdf.orientation='L'
    #pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", size=10)

    # Spaltenüberschriften hinzufügen
    for col in df.columns:
        pdf.cell(45, 8, col, 1)
    pdf.ln()

    # Daten hinzufügen
    for index, row in df.iterrows():
        for col in df.columns:
            pdf.cell(45, 5, str(row[col]), 1)
        pdf.ln()

    pdf.output(pdf_filename)

    print(f"PDF wurde erfolgreich erstellt: {pdf_filename}")


# In[6]:


def create_csv_from_dataframe(df, csv_filename):

    df.to_csv(csv_filename, index=False)

    print(f"CSV wurde erfolgreich erstellt: {csv_filename}")


# In[7]:


# Funktion zum Zusammenführen der Werte einer Zeile zu einem String
def merge_values(row):
    return row['termin'] + ' #' + str(row['teil'])


# In[ ]:


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':

        # Eingabedaten aus Request einlesen
        csv_dateipfad_in = request.form['csv_dateipfad_in']
        postfix = request.form['postfix']
        eingabedatum = request.form['eingabedatum']
        reminder = request.form['reminder']
        #eingabedatum = "2023-12-31"

        print(eingabedatum)

        #PROD auf pythonanywhere
        path = "/home/alexontour/mysite/download/"
        path_in = "/home/alexontour/mysite/"
        # DEV - Local
        path = "download/"
        path_in =""


        # Datum/ Schema-CSV-Datei in DataFrame lesen
        df = pd.read_csv(path_in + csv_dateipfad_in, encoding='latin1', sep=';')
        for index, row in df.iterrows():
            # Ändere den Wert in der Spalte 'Alter'
            wochen_zukunft = int(df.at[index, 'offset'])*4
            #eingabedatum_temp_obj = datetime.strptime(eingabedatum, "%d.%m.%Y")
            #eingabedatum = eingabedatum_temp_obj.strftime("%Y-%m-%d")
            startdatum, enddatum = kalenderwochen_start_end_datum(eingabedatum, wochen_zukunft)
            #startdatum = str(startdatum)
            #enddatum = str(enddatum)
            df.at[index, 'start'] = startdatum
            df.at[index, 'end'] = enddatum
            # Neue Spalte hinzufügen, die die zusammengeführten Strings enthält
            df['beschreibung'] = df.apply(merge_values, axis=1)
            df['beschreibung'] = df['beschreibung'] + " (" + postfix + ")"
            df['reminder'] = reminder

        # DataFrame anzeigen
        print(df)
        df = df.fillna("")
        df = df.astype(str)


        # Erzeuge ICS-Datei
        ics_filename = path + "impfplan-" + eingabedatum + ".ics"
        create_ics_from_dataframe(df, ics_filename)

        # für den Druck optimieren: nicht relevante Spalten löschen, neu ordnen & Datum formatieren
        df = df.drop(['termin', 'teil', 'reminder'], axis=1)
        new_order = ['beschreibung', 'offset','info']
        df = df[new_order]
        #df['start'] = pd.to_datetime(df['start']).dt.strftime('%d.%m.%Y')
        #df['end'] = pd.to_datetime(df['end']).dt.strftime('%d.%m.%Y')
        df['erledigt'] = " "


        # Erzeuge CSV-Datei
        csv_filename = path + "impfplan-" + eingabedatum + ".csv"
        create_csv_from_dataframe(df, csv_filename)

        # Erzeuge PDF-Datei
        pdf_filename = path + "impfplan-" + eingabedatum + ".pdf"
        create_pdf_from_dataframe(df, pdf_filename)

        # Downlaod-Seite rendern
        return render_template('download.html',
                        pdf_filename=os.path.basename(pdf_filename),
                        csv_filename=os.path.basename(csv_filename),
                        ics_filename=os.path.basename(ics_filename))


@app.route('/download/<filename>')
def download(filename):
    #PROD
    path = "/home/alexontour/mysite/download/"
    #DEV
    path = "download/"
    return send_file(path + filename, as_attachment=True)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(port=5000)


