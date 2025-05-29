# NatuurSpotter/geocode.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")


def geocode_place(place: str):
    if not API_KEY or not place:
        return None, None

    params = {
        "key": API_KEY,
        "q": place,
        "countrycode": "BE",
        "limit": 1,
        "language": "nl"
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
