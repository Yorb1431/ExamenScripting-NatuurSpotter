from flask import Flask, render_template, request
from NatuurSpotter.db import get_cached, get_species_info, save_species_info, cache_daylist
from NatuurSpotter.geocode import geocode_place
from NatuurSpotter.naming import to_latin, to_common
from datetime import datetime
from NatuurSpotter.scraper import fetch_data

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    data = []
    selected_date = ""
    if request.method == "POST":
        selected_date = request.form.get("date")
        try:
            datetime.strptime(selected_date, "%Y-%m-%d")
        except ValueError:
            return render_template("index.html", data=[], error="Ongeldige datum", selected_date=selected_date)

        cached_data = get_cached(selected_date)
        if cached_data:
            data = cached_data
        else:
            scraped_data = fetch_data(selected_date)
            for obs in scraped_data:
                lat, lon = geocode_place(obs["place"])
                obs["lat"] = lat
                obs["lon"] = lon

                species = obs.get("common_name", "").strip()
                species_info = get_species_info(species)

                if not species_info:
                    latin_name = to_latin(species)
                    if latin_name.lower() == species.lower() or latin_name.lower() == "onbekend":
                        latin_name = obs["latin_name"]
                        common_name = to_common(latin_name)
                    else:
                        common_name = species

                    save_species_info(common_name, latin_name,
                                      obs["description"])
                    obs["common_name"] = common_name
                    obs["latin_name"] = latin_name
                else:
                    obs["common_name"] = species_info["common_name"]
                    obs["latin_name"] = species_info["latin_name"]

            cache_daylist(selected_date, scraped_data)
            data = scraped_data

    return render_template("index.html", data=data, selected_date=selected_date)
