# NatuurSpotter/app.py

import os
from flask import Flask, render_template, request
from NatuurSpotter.scraper import scrape_daylist
from NatuurSpotter.db import get_cached, cache_daylist

app = Flask(__name__)
SPECIES_GROUP = 16
COUNTRY_DIVISION = 23


@app.route("/", methods=["GET", "POST"])
def index():
    lang = request.values.get("lang", "nl")
    date = request.values.get("date", "")
    observations = None
    heat_coords = []

    if request.method == "POST" and date:
        # kijk in cache
        cache = get_cached(date)
        if cache:
            observations = cache
        else:
            fresh = scrape_daylist(date, SPECIES_GROUP, COUNTRY_DIVISION)
            cache_daylist(date, fresh)
            observations = fresh

    # bouw heatmap-coördinaten als we lat/lon hadden
    # heat_coords = [(o["lat"],o["lon"]) for o in observations if o.get("lat") and o.get("lon")]

    return render_template(
        "index.html",
        lang=lang,
        date=date,
        observations=observations or [],
        heat_coords=heat_coords
    )


if __name__ == "__main__":
    app.run(debug=True)
