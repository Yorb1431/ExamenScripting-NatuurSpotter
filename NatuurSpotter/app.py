# NatuurSpotter/app.py

from flask import Flask, render_template, request
from NatuurSpotter.db import get_cached, get_species_info, save_species_info, cache_daylist
from NatuurSpotter.naming import to_latin, to_common
from datetime import datetime
import os

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    lang = request.values.get("lang", "nl")
    date = request.form.get("date") if request.method == "POST" else ""
    observations = []
    heat_coords = []

    if request.method == "POST" and date:
        cached = get_cached(date)
        for obs in cached:
            species = obs["species"]
            info = get_species_info(species)

            # Als info ontbreekt, gebruik AI om de ontbrekende naam aan te vullen
            if not info:
                latin = species
                common = to_common(latin)
                save_species_info(common, latin)
            else:
                latin = info["latin_name"]
                common = info["common_name"]

                # Als de namen gelijk zijn, gebruik AI om common te verbeteren
                if common == latin or common.lower() == "unknown":
                    common = to_common(latin)
                    save_species_info(common, latin)

            obs["common_name"] = common
            obs["latin_name"] = latin
            obs["description"] = info["description"] if info and info["description"] else ""

            # Voeg coördinaten toe aan heatmap als ze bestaan
            if obs["lat"] and obs["lon"]:
                heat_coords.append([float(obs["lat"]), float(obs["lon"])])

            obs["date"] = obs["obs_date"].strftime(
                "%Y-%m-%d") if isinstance(obs["obs_date"], datetime) else obs["obs_date"]
            observations.append(obs)

    return render_template("index.html", observations=observations, date=date, lang=lang, heat_coords=heat_coords)


if __name__ == "__main__":
    app.run(debug=True)
