# NatuurSpotter/app.py

from flask import Flask, render_template, request
from NatuurSpotter.scraper import scrape_daylist
from NatuurSpotter.db import (
    get_cached,
    cache_daylist,
    update_description,
    get_species_info,
    save_species_info
)
from NatuurSpotter.wiki import scrape_wikipedia
from NatuurSpotter.naming import to_latin
import folium
from NatuurSpotter.geocode import geocode_place
import random
from folium.plugins import HeatMap

app = Flask(__name__)
SPECIES_GROUP = 16
COUNTRY_DIVISION = 23


@app.route("/", methods=["GET", "POST"])
def index():
    date = None
    lang = request.values.get("lang", "nl")
    observations = []

    if request.method == "POST":
        date = request.form.get("date")
        lang = request.form.get("lang", "nl")

        if date:
            # 1) Probeer eerst uit cache te halen
            cached = get_cached(date)
            if cached:
                observations = cached
            else:
                # 2) Anders fresh scrapen
                fresh = scrape_daylist(date, SPECIES_GROUP, COUNTRY_DIVISION)
                # Zorg dat alle velden bestaan
                for rec in fresh:
                    rec.setdefault("latin_name", None)
                    rec.setdefault("description", None)
                    rec.setdefault("photo_link", None)
                # In cache opslaan
                cache_daylist(date, fresh)
                observations = fresh

            # 3) Vul per record latin_name + description aan
            for obs in observations:
                info = get_species_info(obs["common_name"])
                if info:
                    obs["latin_name"] = info["latin_name"]
                    obs["description"] = info["description"]
                else:
                    wiki_data = scrape_wikipedia(obs["common_name"])
                    latin = to_latin(obs["common_name"])
                    description = wiki_data.get("description") or ""
                    save_species_info(obs["common_name"], latin, description)
                    obs["latin_name"] = latin
                    obs["description"] = description
                    update_description(date, obs["common_name"], description)

    # === Maak de Folium‐map ===
    # Center in Henegouwen (Hainaut) – ongeveer [50.5, 3.8]
    # Kies een donker thema (CartoDB Dark Matter)
    folium_map = folium.Map(
        location=[50.5, 3.8],
        zoom_start=9,
        tiles="CartoDB Dark_Matter"
    )

    # Generate random points in Hainaut for each observation
    # Hainaut bounding box: lat 50.1–50.8, lon 3.1–4.5 (wider spread)
    heat_data = []
    for obs in observations:
        for _ in range(int(obs.get("count", 1))):
            lat = random.uniform(50.1, 50.8)
            lon = random.uniform(3.1, 4.5)
            heat_data.append([lat, lon])

    if heat_data:
        HeatMap(heat_data, radius=10, blur=18, min_opacity=0.3, max_zoom=12).add_to(folium_map)

    folium_map_html = folium_map._repr_html_()

    return render_template(
        "index.html",
        date=date,
        lang=lang,
        observations=observations,
        folium_map=folium_map_html
    )


if __name__ == "__main__":
    app.run(debug=True)
