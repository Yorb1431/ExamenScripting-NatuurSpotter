# NatuurSpotter/wiki.py

import requests
from bs4 import BeautifulSoup


def scrape_wikipedia(common_name: str) -> dict:
    slug = common_name.replace(" ", "_")
    url = f"https://nl.wikipedia.org/wiki/{slug}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1", id="firstHeading").get_text(strip=True)
        p = soup.select_one("div#mw-content-text p")
        description = p.get_text(strip=True) if p else ""
        return {"common": title, "description": description}
    except:
        return {"common": common_name, "description": "Geen info gevonden."}
