import requests
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


def geocode_place(place):
    url = "https://forward-reverse-geocoding.p.rapidapi.com/v1/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "forward-reverse-geocoding.p.rapidapi.com"
    }
    params = {
        "q": place,
        "accept-language": "nl",
        "polygon_threshold": 0.0
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            return None, None
    except Exception as e:
        print(f"Geocoding error for '{place}': {e}")
        return None, None
