# NatuurSpotter/analysis.py
# Analyse functionaliteit voor NatuurSpotter
# Bevat functies voor data-analyse, visualisatie en rapportgeneratie

import folium
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Image, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from NatuurSpotter.db import connection
import openai
from dotenv import load_dotenv

load_dotenv()

# Maak output directory aan voor gegenereerde bestanden
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def soort_info(soort, soortgroep):
    # Toont gedetailleerde informatie over een specifieke soort
    # Genereert een PDF rapport met soortinformatie en recente waarnemingen
    cursor = connection.cursor()
    
    # Controleer of de soort tot de toegewezen soortgroep behoort
    cursor.execute("""
        SELECT * FROM soorten 
        WHERE naam = %s AND soortgroep = %s
    """, (soort, soortgroep))
    
    soort_data = cursor.fetchone()
    if not soort_data:
        return f"De soort {soort} behoort niet tot de soortgroep {soortgroep}"
    
    # Haal de 10 recentste waarnemingen op
    cursor.execute("""
        SELECT o.*, s.naam as soort_naam 
        FROM observaties o
        JOIN soorten s ON o.soort_id = s.id
        WHERE s.naam = %s
        ORDER BY o.datum DESC
        LIMIT 10
    """, (soort,))
    
    recente_waarnemingen = cursor.fetchall()
    
    # Genereer PDF rapport met tabel en afbeelding
    pdf_filename = f"rapport_{soort}_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Voeg titel, afbeelding, latijnse naam en beschrijving toe
    elements.append(Paragraph(f"<b>{soort_data['naam']}</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Voeg afbeelding toe indien beschikbaar
    if soort_data.get('photo_link'):
        try:
            import requests
            from io import BytesIO
            response = requests.get(soort_data['photo_link'])
            if response.status_code == 200:
                img = Image(BytesIO(response.content), width=200, height=150)
                elements.append(img)
                elements.append(Spacer(1, 12))
        except Exception:
            pass
    
    # Voeg soortinformatie toe
    elements.append(Paragraph(f"<b>Latijnse naam:</b> {soort_data['latijnse_naam']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Zeldzaamheidsstatus:</b> {soort_data['zeldzaamheid']}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Voeg beschrijving toe
    elements.append(Paragraph(soort_data['beschrijving'], styles['BodyText']))
    elements.append(Spacer(1, 18))
    
    # Voeg tabel met recente waarnemingen toe
    data = [["Datum", "Aantal", "Locatie"]]
    for w in recente_waarnemingen:
        data.append([str(w['datum']), str(w.get('aantal', 1)), w.get('locatie', '-')])
    t = Table(data, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(t)
    
    doc.build(elements)
    
    return {
        'soort_info': soort_data,
        'recente_waarnemingen': recente_waarnemingen,
        'pdf_rapport': pdf_filename
    }

def soort_observaties_csv(soort):
    # Genereert een CSV-bestand met de 10 recentste waarnemingen van een soort
    cursor = connection.cursor()
    cursor.execute("""
        SELECT o.datum, o.aantal, o.locatie
        FROM observaties o
        JOIN soorten s ON o.soort_id = s.id
        WHERE s.naam = %s
        ORDER BY o.datum DESC
        LIMIT 10
    """, (soort,))
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    csv_filename = f"recent_waarnemingen_{soort}_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(csv_filename, index=False)
    return csv_filename

def observaties_kaart(dag=None):
    # Genereert een interactieve kaart met waarnemingen voor een specifieke dag
    if dag is None:
        dag = date.today()
    
    cursor = connection.cursor()
    
    # Haal alle waarnemingen op voor de gegeven dag
    cursor.execute("""
        SELECT o.*, s.naam as soort_naam, s.soortgroep
        FROM observaties o
        JOIN soorten s ON o.soort_id = s.id
        WHERE DATE(o.datum) = %s
    """, (dag,))
    
    waarnemingen = cursor.fetchall()
    if not waarnemingen:
        # Geen data, maak een placeholder bestand
        placeholder_path = os.path.join(OUTPUT_DIR, f"geen_kaart_{dag}.html")
        with open(placeholder_path, 'w', encoding='utf-8') as f:
            f.write(f"<html><body><h2>Geen waarnemingen gevonden voor {dag}.</h2></body></html>")
        return placeholder_path
    
    # Maak een nieuwe kaart gecentreerd op België
    m = folium.Map(location=[51.1657, 4.4317], zoom_start=8)
    
    # Definieer kleuren voor verschillende soortgroepen
    kleuren = {
        'Vogels': 'red',
        'Vlinders': 'blue',
        'Planten': 'green',
        'Zoogdieren': 'purple'
    }
    
    # Voeg markers toe voor elke waarneming
    for waarneming in waarnemingen:
        kleur = kleuren.get(waarneming['soortgroep'], 'gray')
        folium.Marker(
            location=[waarneming['latitude'], waarneming['longitude']],
            popup=f"{waarneming['soort_naam']} - {waarneming['datum']}",
            icon=folium.Icon(color=kleur)
        ).add_to(m)
    
    # Sla de kaart op
    kaart_bestand = os.path.join(OUTPUT_DIR, f"waarnemingen_kaart_{dag}.html")
    m.save(kaart_bestand)
    
    return kaart_bestand

def seizoensanalyse(soort, jaar):
    # Analyseert seizoensgebonden patronen in waarnemingen
    # Genereert een grafiek en wetenschappelijke analyse
    cursor = connection.cursor()
    
    # Haal alle waarnemingen op voor de gegeven soort en jaar
    cursor.execute("""
        SELECT MONTH(datum) as maand, COUNT(*) as aantal
        FROM observaties o
        JOIN soorten s ON o.soort_id = s.id
        WHERE s.naam = %s AND YEAR(datum) = %s
        GROUP BY MONTH(datum)
        ORDER BY maand
    """, (soort, jaar))
    
    data = cursor.fetchall()
    
    # Maak een DataFrame en genereer grafiek
    df = pd.DataFrame(data, columns=['maand', 'aantal'])
    plt.figure(figsize=(12, 6))
    sns.barplot(x='maand', y='aantal', data=df)
    plt.title(f'Waarnemingen van {soort} in {jaar}')
    plt.xlabel('Maand')
    plt.ylabel('Aantal waarnemingen')
    
    # Sla de grafiek op
    grafiek_bestand = f"seizoensanalyse_{soort}_{jaar}.png"
    plt.savefig(grafiek_bestand)
    plt.close()
    
    # Gebruik OpenAI voor wetenschappelijke analyse
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Je bent een expert in ecologie en biodiversiteit."},
            {"role": "user", "content": f"Waarom wordt de soort {soort} in bepaalde seizoenen minder waargenomen? Geef een wetenschappelijke analyse."}
        ]
    )
    
    return {
        'grafiek': grafiek_bestand,
        'analyse': response.choices[0].message.content
    }

def biodiversiteit_analyse(maand=None, jaar=None):
    # Analyseert biodiversiteitsgegevens per maand in een jaar
    # Berekent soortenrijkdom en waarnemingsfrequentie
    if maand is None:
        maand = datetime.now().month
    if jaar is None:
        jaar = datetime.now().year
    
    cursor = connection.cursor()
    
    # Haal alle waarnemingen op voor de gegeven periode
    cursor.execute("""
        SELECT s.naam, s.soortgroep, COUNT(*) as aantal_waarnemingen
        FROM observaties o
        JOIN soorten s ON o.soort_id = s.id
        WHERE MONTH(o.datum) = %s AND YEAR(o.datum) = %s
        GROUP BY s.naam, s.soortgroep
        ORDER BY aantal_waarnemingen DESC
    """, (maand, jaar))
    
    data = cursor.fetchall()
    
    # Maak een DataFrame en bereken statistieken
    df = pd.DataFrame(data, columns=['soort', 'soortgroep', 'aantal_waarnemingen'])
    soortenrijkdom = len(df)
    waarnemingsfrequentie = df['aantal_waarnemingen'].mean() if not df.empty else 0
    dominante_soort = df.iloc[0]['soort'] if not df.empty else 'Geen data'
    
    # Genereer tabel
    tabel_bestand = os.path.join(OUTPUT_DIR, f"biodiversiteit_tabel_{maand}_{jaar}.csv")
    df.to_csv(tabel_bestand, index=False)
    
    return {
        'soortenrijkdom': soortenrijkdom,
        'waarnemingsfrequentie': waarnemingsfrequentie,
        'dominante_soort': dominante_soort,
        'tabel': tabel_bestand
    } 