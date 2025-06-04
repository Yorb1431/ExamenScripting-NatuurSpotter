# NatuurSpotter/app.py

from flask import Flask, render_template, request, send_file, make_response
from NatuurSpotter.scraper import scrape_daylist, scrape_all_observations
from NatuurSpotter.db import (
    get_cached,
    cache_daylist,
    update_description,
    get_species_info,
    save_species_info
)
from NatuurSpotter.wiki import scrape_wikipedia
from NatuurSpotter.naming import to_latin
from NatuurSpotter.analysis import soort_info, observaties_kaart, seizoensanalyse, biodiversiteit_analyse, soort_observaties_csv
import folium
from NatuurSpotter.geocode import geocode_place
import random
from folium.plugins import HeatMap
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import urllib.parse
import os
import requests

app = Flask(__name__)
SPECIES_GROUP = 16
COUNTRY_DIVISION = 23

# Add output directory constant
OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route("/", methods=["GET", "POST"])
def index():
    date = None
    lang = request.values.get("lang", "nl")
    observations = []

    if request.method == "POST":
        date = request.form.get("date")
        lang = request.form.get("lang", "nl")

        if date:
            # 1) Probeer eerst uit cache/DB te halen
            cached = get_cached(date)
            if cached:
                observations = cached
            else:
                # 2) Anders scrape alle waarnemingen (alle soorten)
                observations = scrape_daylist(date, SPECIES_GROUP, COUNTRY_DIVISION)
                # cache_daylist(date, observations)

    # Als er geen datum is gekozen, toon niets of vandaag
    # (optioneel: je kan ook default vandaag tonen)

    # === Maak de Folium‐map ===
    folium_map_html = None
    if observations:
        folium_map = folium.Map(
            location=[50.5, 3.8],
            zoom_start=9,
            tiles="CartoDB Dark_Matter"
        )
        heat_data = []
        for obs in observations:
            # Gebruik lat/lon als beschikbaar, anders random
            lat = obs.get("lat") or random.uniform(50.1, 50.8)
            lon = obs.get("lon") or random.uniform(3.1, 4.5)
            heat_data.append([lat, lon])
        if heat_data:
            HeatMap(heat_data, radius=10, blur=18, min_opacity=0.3,
                    max_zoom=12).add_to(folium_map)
        folium_map_html = folium_map._repr_html_()

    # === Biodiversiteit berekenen ===
    soorten = set(obs["species"] if "species" in obs else obs["common_name"]
                  for obs in observations)
    soortenrijkdom = len(soorten)
    waarnemingsfrequentie = len(observations) / \
        soortenrijkdom if soortenrijkdom else 0

    return render_template(
        "index.html",
        date=date,
        lang=lang,
        observations=observations,
        folium_map=folium_map_html,
        soortenrijkdom=soortenrijkdom,
        waarnemingsfrequentie=waarnemingsfrequentie
    )


@app.route("/soort_info/<soort>")
def soort_info_route(soort):
    resultaat = soort_info(soort, SPECIES_GROUP)
    if isinstance(resultaat, str):
        return resultaat
    return render_template(
        "soort_info.html",
        soort_info=resultaat['soort_info'],
        recente_waarnemingen=resultaat['recente_waarnemingen'],
        pdf_rapport=resultaat['pdf_rapport']
    )


@app.route("/observaties_kaart")
def observaties_kaart_route():
    dag = request.args.get('dag')
    if dag:
        dag = datetime.strptime(dag, '%Y-%m-%d').date()
    kaart_bestand = observaties_kaart(dag)
    return send_file(kaart_bestand)


@app.route("/seizoensanalyse/<soort>/<int:jaar>")
def seizoensanalyse_route(soort, jaar):
    resultaat = seizoensanalyse(soort, jaar)
    return render_template(
        "seizoensanalyse.html",
        soort=soort,
        jaar=jaar,
        grafiek=resultaat['grafiek'],
        analyse=resultaat['analyse']
    )


@app.route("/biodiversiteit")
def biodiversiteit_route():
    maand = request.args.get('maand', type=int)
    jaar = request.args.get('jaar', type=int)
    resultaat = biodiversiteit_analyse(maand, jaar)
    return render_template(
        "biodiversiteit.html",
        maand=maand or datetime.now().month,
        jaar=jaar or datetime.now().year,
        soortenrijkdom=resultaat['soortenrijkdom'],
        waarnemingsfrequentie=resultaat['waarnemingsfrequentie'],
        dominante_soort=resultaat['dominante_soort'],
        tabel=resultaat['tabel']
    )


@app.route("/soort_info/<soort>/pdf")
def download_soort_pdf(soort):
    resultaat = soort_info(soort, SPECIES_GROUP)
    return send_file(resultaat['pdf_rapport'], as_attachment=True)


@app.route("/soort_info/<soort>/csv")
def download_soort_csv(soort):
    csv_file = soort_observaties_csv(soort)
    return send_file(csv_file, as_attachment=True)


@app.route("/download_csv", methods=["POST"])
def download_csv():
    date = request.form.get("date")
    # Try DB first, else scrape
    cached = get_cached(date)
    if cached:
        observations = cached
    else:
        observations = scrape_daylist(date, SPECIES_GROUP, COUNTRY_DIVISION)

    if not observations:
        return "Geen data beschikbaar voor deze dag.", 404

    # Use all keys present in any observation
    all_keys = set()
    for obs in observations:
        all_keys.update(obs.keys())
    all_keys = list(all_keys)
    df = pd.DataFrame(observations, columns=all_keys)
    csv_data = df.to_csv(index=False)

    # Save CSV to output directory
    filename = f"waarnemingen_{date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(csv_data)

    response = make_response(csv_data)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv"
    return response


@app.route("/download_pdf/<species>/<date>/<observer>")
def download_pdf(species, date, observer):
    # URL decode
    species = urllib.parse.unquote(species)
    observer = urllib.parse.unquote(observer)
    date = urllib.parse.unquote(date)
    
    # Get species info including description
    species_info = get_species_info(species)
    if not species_info:
        species_info = scrape_wikipedia(species)
        save_species_info(species, species_info)

    # Get all observations for this species
    cached = get_cached(date)
    if cached:
        all_obs = [o for o in cached if (o.get('species', o.get('common_name', '')).split('-')[0].strip() == species)]
    else:
        all_data = scrape_daylist(date, SPECIES_GROUP, COUNTRY_DIVISION)
        all_obs = [o for o in all_data if (o.get('species', o.get('common_name', '')).split('-')[0].strip() == species)]

    # Get unique locations
    locations = set()
    for obs in all_obs:
        if obs.get('place'):
            locations.add(obs.get('place'))
        elif obs.get('location'):
            locations.add(obs.get('location'))

    # --- Seasonality Graph ---
    months = [o.get('date', '')[5:7] for o in all_obs if o.get('date')]
    graph_img = BytesIO()
    plt.figure(figsize=(6, 3))
    if months:
        # Convert months to seasons
        seasons = []
        for month in months:
            month_num = int(month)
            if month_num in [12, 1, 2]:
                seasons.append('Winter')
            elif month_num in [3, 4, 5]:
                seasons.append('Spring')
            elif month_num in [6, 7, 8]:
                seasons.append('Summer')
            else:
                seasons.append('Autumn')
        
        # Create season count plot
        sns.countplot(x=seasons, order=['Spring', 'Summer', 'Autumn', 'Winter'])
        plt.title(f'Seizoenspatroon van {species}')
        plt.xlabel('Seizoen')
        plt.ylabel('Aantal waarnemingen')
    else:
        plt.text(0.5, 0.5, 'Geen data', ha='center', va='center')
    plt.tight_layout()
    plt.savefig(graph_img, format='png')
    plt.close()
    graph_img.seek(0)

    # --- PDF Generation ---
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"<b>{species}</b>", styles['Title']))
    if species_info.get('latin_name'):
        elements.append(Paragraph(f"<i>{species_info['latin_name']}</i>", styles['Italic']))
    elements.append(Spacer(1, 12))

    # Description
    if species_info.get('description'):
        elements.append(Paragraph("<b>Beschrijving</b>", styles['Heading3']))
        elements.append(Paragraph(species_info['description'], styles['Normal']))
        elements.append(Spacer(1, 12))

    # Locations
    if locations:
        elements.append(Paragraph("<b>Gevonden in</b>", styles['Heading3']))
        for location in sorted(locations):
            elements.append(Paragraph(f"• {location}", styles['Normal']))
        elements.append(Spacer(1, 12))

    # Seasonality
    elements.append(Paragraph("<b>Seizoenspatroon</b>", styles['Heading3']))
    elements.append(Image(graph_img, width=400, height=200))

    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)

    # Save PDF to output directory
    filename = f"{species}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(pdf_buffer.getvalue())

    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')


if __name__ == "__main__":
    app.run(debug=True)
