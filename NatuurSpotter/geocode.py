import requests
import os

RAPIDAPI_HOST = "opencage-geocoder.p.rapidapi.com"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
HEADERS = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY,
}

# bekende fallbackplaatsen
FALLBACKS = {
    "Monceau-Imbrechies (HA)": (50.0663, 4.1459),
    "Marais d'Harchies - Terril d'Hensies (HA)": (50.4567, 3.6906),
    "Macon (HA)": (50.0547, 4.1485),
    "Momignies Life BNIP 24 mares de l'arboretum (HA)": (50.0123, 4.2050),
    "Marais d'Harchies": (50.4700, 3.6950),
    "Les Lacs de l’Eau d’Heure": (50.1500, 4.4000),
    "Pays des Collines": (50.7333, 3.6667),
    "Honnelles": (50.3500, 3.7500),
    "Stambruges": (50.5500, 3.8000),
    "Merbes-le-Château": (50.3000, 4.2000),
    "Bernissart": (50.4500, 3.7000),
    "Solre-sur-Sambre": (50.2500, 4.2000),
    "Beloeil": (50.5500, 3.7000),
    "Mont-de-l’Enclus": (50.7500, 3.5000)
}


def geocode(place):
    if place in FALLBACKS:
        return FALLBACKS[place]

    url = f"https://{RAPIDAPI_HOST}/geocode/v1/json"
    params = {"q": place, "limit": 1}
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        if data["results"]:
            loc = data["results"][0]["geometry"]
            return loc["lat"], loc["lng"]
    except Exception as e:
        print(f"[Geo] Geocoding mislukt voor '{place}': {e}")

    return None, None
