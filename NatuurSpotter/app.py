import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

# onze eigen modules
from NatuurSpotter.db import get_cached, cache_daylist, update_description
from NatuurSpotter.scraper import scrape_daylist
from NatuurSpotter.wiki import generate_description

load_dotenv()

app = Flask(__name__)

# Configuratie constants (Coleoptera = 16, Hainaut = 23)
SPECIES_GROUP = 16
COUNTRY_DIVISION = 23


@app.route("/", methods=["GET", "POST"])
def index():
    lang = request.values.get("lang", "nl")
    date = request.form.get("date")

    observations = []
    heat_coords = []

    if date:
        # Eerst proberen uit cache
        cached = get_cached(date)
        if cached:
            observations = cached
        else:
            # Anders scrapen en cachen
            fresh = scrape_daylist(date, SPECIES_GROUP, COUNTRY_DIVISION)
            cache_daylist(date, fresh)
            observations = fresh

        # Voor elk record: als er nog geen beschrijving is, opvragen & opslaan
        for obs in observations:
            if not obs.get("description"):
                desc = generate_description(obs["latin_name"])
                if desc:
                    update_description(obs["id"], desc)
                    obs["description"] = desc
                else:
                    obs["description"] = "-"

            # kaart coördinaten verzamelen
            if obs.get("lat") and obs.get("lon"):
                try:
                    lat = float(obs["lat"])
                    lon = float(obs["lon"])
                    heat_coords.append([lat, lon])
                except ValueError:
                    pass

    return render_template(
        "index.html",
        observations=observations,
        heat_coords=heat_coords,
        date=date,
        lang=lang
    )


if __name__ == "__main__":
    app.run(debug=True)
