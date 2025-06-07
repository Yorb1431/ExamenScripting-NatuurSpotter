# NatuurSpotter/app.py
# Main voor Exameen
#  Flask en webapp

from flask import Flask, render_template, request, send_file, make_response, jsonify
from NatuurSpotter.scraper import scrape_daylist, scrape_all_observations
from NatuurSpotter.db import (
    get_cached,
    cache_daylist,
    update_description,
    get_species_info,
    save_species_info,
    get_recent_observations
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
from bs4 import BeautifulSoup
from NatuurSpotter.pdf import generate_pdf

app = Flask(__name__)
SPECIES_GROUP = 16  # ID kevers web
COUNTRY_DIVISION = 23  # ID Henegouwen

# Maak  directory aan  gegenereerde bestanden
OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


@app.route("/", methods=["GET", "POST"])
def index():
    # Mainapp
    # Toont waarnemingen voor een gekozen datum met kaart en statistieken
    date = None
    lang = request.values.get("lang", "nl")
    observations = []

    if request.method == "POST":
        date = request.form.get("date")
        lang = request.form.get("lang", "nl")

        if date:
            # Probeer eerst uit cache/DB te halen
            cached = get_cached(date)
            if cached:
                observations = cached
            else:
                #  Anders scrape alle waarneminge
                observations = scrape_daylist(
                    date, SPECIES_GROUP, COUNTRY_DIVISION)
                # cache_daylist(date, observations)

    # Maak map
    folium_map_html = None
    if observations:
        folium_map = folium.Map(
            location=[50.5, 3.8],  # Afbakening Henegouwen
            zoom_start=9,
            tiles="CartoDB Dark_Matter"
        )
        heat_data = []
        for obs in observations:
            lat = obs.get("lat") or random.uniform(50.1, 50.8)
            lon = obs.get("lon") or random.uniform(3.1, 4.5)
            heat_data.append([lat, lon])
        if heat_data:
            HeatMap(heat_data, radius=10, blur=18, min_opacity=0.3,
                    max_zoom=12).add_to(folium_map)
        folium_map_html = folium_map._repr_html_()

    # Biodiversiteit
    soorten = set(obs["species"] if "species" in obs else obs["common_name"]
                  for obs in observations)
    soortenrijkdom = len(soorten)
    waarnemingsfrequentie = len(observations) / \
        soortenrijkdom if soortenrijkdom else 0

    # save CSV
    if observations:
        csv_dir = os.path.join(OUTPUT_DIR, "csv")
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)

        # Use all keys observation
        all_keys = set()
        for obs in observations:
            all_keys.update(obs.keys())
        all_keys = list(all_keys)
        df = pd.DataFrame(observations, columns=all_keys)
        csv_data = df.to_csv(index=False)

        filename = f"waarnemingen_{date}.csv"
        filepath = os.path.join(csv_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        print(f"CSV saved to: {filepath}")

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
    # Toont informatie over een specifieke soort
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
    # Genereert het kaart  waarnemingen per  dag
    dag = request.args.get('dag')
    if dag:
        dag = datetime.strptime(dag, '%Y-%m-%d').date()
    kaart_bestand = observaties_kaart(dag)
    return send_file(kaart_bestand)


@app.route("/seizoensanalyse/<soort>/<int:jaar>")
def seizoensanalyse_route(soort, jaar):
    # Toont seizoensanalyse
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
    # Toont biodiversiteitsanalyse
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
    # Download PDF
    resultaat = soort_info(soort, SPECIES_GROUP)
    return send_file(resultaat['pdf_rapport'], as_attachment=True)


@app.route("/soort_info/<soort>/csv")
def download_soort_csv(soort):
    # Download CSV
    csv_file = soort_observaties_csv(soort)
    return send_file(csv_file, as_attachment=True)


@app.route("/download_pdf/<species>/<date>/<observer>")
def download_pdf(species, date, observer):
    try:
        print(
            f"Starting PDF generation for species: {species}, date: {date}, observer: {observer}")

        species_info = get_species_info(species)
        print(f"Species info from DB: {species_info}")

        if not species_info:
            print("No species info found in DB, trying Wikipedia...")
            species_info = scrape_wikipedia(species)
            print(f"Species info from Wikipedia: {species_info}")
            if species_info:
                print("Saving species info to DB...")
                save_species_info(
                    common_name=species,
                    latin_name=species_info.get('latin_name', ''),
                    description=species_info.get('description', ''),
                    photo_link=species_info.get('photo_link', '')
                )

        print(f"Getting observations for date: {date}")
        cached = get_cached(date)
        print(f"Cached observations: {cached}")

        if cached:
            all_obs = [o for o in cached if (o.get('species', o.get(
                'common_name', '')).split('-')[0].strip() == species)]
        else:
            print("No cached observations, scraping daylist...")
            all_data = scrape_daylist(date, SPECIES_GROUP, COUNTRY_DIVISION)
            all_obs = [o for o in all_data if (o.get('species', o.get(
                'common_name', '')).split('-')[0].strip() == species)]

        print(f"Filtered observations: {all_obs}")

        # Generate PDF
        print("Generating PDF...")
        pdf_buffer, filename = generate_pdf(
            species, date, observer, species_info, all_obs)
        print(f"PDF generated successfully: {filename}")

        return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
    except Exception as e:
        print(f"Error in download_pdf: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return f"Error generating PDF: {str(e)}", 500


@app.route("/api/observaties", methods=["GET"])
def api_observaties():
    # API endpoint voor het ophalen van recente waarnemingen
    data = get_recent_observations(limit=10)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
