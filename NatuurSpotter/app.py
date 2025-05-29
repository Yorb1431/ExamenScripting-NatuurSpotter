# NatuurSpotter/app.py

from flask import Flask, render_template, request
from NatuurSpotter.db import get_cached, cache_daylist
from NatuurSpotter.scraper import scrape_daylist
from NatuurSpotter.geocode import geocode_place
from NatuurSpotter.naming import to_latin
from NatuurSpotter.wiki import get_description

app = Flask(__name__)

SPECIES_GROUP = 16
COUNTRY_DIVISION = 23
DEFAULT_LAT, DEFAULT_LON = 50.5, 4.1


@app.route("/", methods=["GET", "POST"])
def index():
    lang = request.args.get("lang", "nl")
    date = None
    observations = []
    heat_coords = []

    if request.method == "POST":
        date = request.form["date"]
        # 1) uit cache?
        cached = get_cached(date)
        if cached:
            observations = cached
            heat_coords = [
                (obs["lat"] or DEFAULT_LAT, obs["lon"] or DEFAULT_LON)
                for obs in cached
            ]
        else:
            # 2) fresh scrape
            raw = scrape_daylist(date, SPECIES_GROUP, COUNTRY_DIVISION)
            for r in raw:
                common = r["common_name"]
                latin = to_latin(common)
                desc = get_description(common, latin)
                lat, lon = geocode_place(r["place"])
                rec = {
                    "obs_date": date,
                    "count": r["count"],
                    "common_name": common,
                    "latin_name": latin,
                    "description": desc,
                    "place": r["place"],
                    "observer": r["observer"],
                    "photo_link": r["photo_link"],
                    "lat": lat,
                    "lon": lon
                }
                observations.append(rec)
                heat_coords.append((lat or DEFAULT_LAT, lon or DEFAULT_LON))

            cache_daylist(date, observations)

    return render_template(
        "index.html",
        lang=lang,
        date=date,
        observations=observations,
        heat_coords=heat_coords
    )


if __name__ == "__main__":
    app.run(debug=True)
