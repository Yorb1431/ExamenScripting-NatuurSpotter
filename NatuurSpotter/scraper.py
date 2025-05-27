# NatuurSpotter/scraper.py

import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# eenvoudig .env-bestand inladen
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key, val)

INAT_TOKEN = os.getenv("INAT_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "opencage-geocoder.p.rapidapi.com"
RAPIDAPI_HEADERS = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}


def scrape_daylist(date, species_group, country_division):
    url = "https://waarnemingen.be/fieldwork/observations/daylist/"
    params = {
        "date":             date,
        "species_group":    species_group,
        "country_division": country_division,
        "rarity":           "",
        "search":           ""
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("table.table-bordered.table-striped tbody tr")

    out = []
    for row in rows:
        cols = row.find_all("td")
        raw = cols[3].get_text(strip=True)
        species = raw.split("-", 1)[-1].strip()
        place = cols[4].get_text(strip=True)
        lat, lon = geocode(place)
        out.append({
            "count":    cols[0].get_text(strip=True),
            "species":  species,
            "place":    place,
            "observer": cols[5].get_text(strip=True),
            "date":     date,
            "lat":      lat,
            "lon":      lon
        })
    return out


def fetch_inaturalist(date, taxon_id, place_id):
    url = "https://api.inaturalist.org/v1/observations"
    headers = {"Authorization": f"Bearer {INAT_TOKEN}"}
    params = {
        "taxon_id":  taxon_id,
        "place_id":  place_id,
        "on":        date,
        "per_page":  50
    }
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    data = r.json().get("results", [])

    out = []
    for item in data:
        species = item.get("species_guess") or item["taxon"]["name"]
        loc = item.get("location", "")
        lat = lon = None
        if "," in loc:
            a, b = loc.split(",", 1)
            try:
                lat, lon = float(a), float(b)
            except ValueError:
                pass
        photos = item.get("photos", [])
        media = photos[0]["url"] if photos else None
        out.append({
            "species":   species,
            "date":      item.get("observed_on"),
            "lat":       lat,
            "lon":       lon,
            "media_url": media,
            "source":    "iNaturalist"
        })
    return out


def geocode(place):
    url = f"https://{RAPIDAPI_HOST}/geocode/v1/json"
    params = {"q": place, "limit": 1}
    try:
        r = requests.get(url, headers=RAPIDAPI_HEADERS, params=params)
        r.raise_for_status()
    except requests.HTTPError:
        return None, None
    results = r.json().get("results", [])
    if not results:
        return None, None
    geo = results[0]["geometry"]
    return geo.get("lat"), geo.get("lng")


if __name__ == "__main__":
    test_date = "2025-05-27"

    print("Daylist + geocode:")
    for o in scrape_daylist(test_date, 16, 23):
        print(o)

    print("\niNaturalist:")
    for o in fetch_inaturalist(test_date, 47126, 9832):
        print(o)
