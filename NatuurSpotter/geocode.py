# NatuurSpotter/geocode.py
# Geocoding functionaliteit voor NatuurSpotter
# Zet plaatsnamen om naar coördinaten met behulp van de OpenCage API

import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")


def geocode_place(place: str):
    # Zet een plaatsnaam om naar coördinaten (latitude/longitude)
    # Gebruikt de OpenCage API voor geocoding
    # Retourneert (None, None) als de plaats niet gevonden kan worden
    if not API_KEY or not place:
        return None, None

    # Stel API parameters in
    params = {
        "key": API_KEY,
        "q": place,
        "countrycode": "BE",  # Alleen zoeken in België
        "limit": 1,  # Alleen het beste resultaat
        "language": "nl"  # Nederlandse resultaten
    }
    url = "https://api.opencagedata.com/geocode/v1/json"
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        if data["results"]:
            geom = data["results"][0]["geometry"]
            return geom["lat"], geom["lng"]
    except Exception:
        pass

    return None, None
