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

app = Flask(__name__)
SPECIES_GROUP = 16
COUNTRY_DIVISION = 23


@app.route("/", methods=["GET", "POST"])
def index():
    date = None
    lang = request.values.get("lang", "nl")
    observations = None

    if request.method == "POST":
        date = request.form.get("date")
        lang = request.form.get("lang", "nl")
        if date:
            # 1) probeer cache
            cached = get_cached(date)
            if cached:
                observations = cached
            else:
                # 2) fresh scrape
                fresh = scrape_daylist(date, SPECIES_GROUP, COUNTRY_DIVISION)
                # zorg dat keys bestaan
                for rec in fresh:
                    rec.setdefault("latin_name", None)
                    rec.setdefault("description", None)
                    rec.setdefault("photo_link", None)
                cache_daylist(date, fresh)
                observations = fresh

            # 3) vul voor elk record de latin_name & description
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

    # heatmap‐coördinaten
    heat_coords = [
        (o["lat"], o["lon"])
        for o in (observations or [])
        if o.get("lat") and o.get("lon")
    ]

    return render_template(
        "index.html",
        date=date,
        lang=lang,
        observations=observations,
        heat_coords=heat_coords
    )


if __name__ == "__main__":
    app.run(debug=True)
