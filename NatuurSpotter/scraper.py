# NatuurSpotter/scraper.py

import requests
from bs4 import BeautifulSoup

# Basis-URL om links compleet te maken
BASE_URL = "https://waarnemingen.be"


def scrape_daylist(date: str, species_group: int, country_division: int):
    """
    Scrape de daglijst van waarnemingen voor een bepaalde datum, 
    soortengroep en provincie. Retourneert een lijst dicts met:
    count, common_name, latin_name, description (None), place, observer, photo_link.
    """
    url = (
        f"{BASE_URL}/fieldwork/observations/daylist/"
        f"?date={date}"
        f"&species_group={species_group}"
        f"&country_division={country_division}"
        f"&rarity=&search="
    )
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    records = []
    for tr in soup.select("tbody tr"):
        # Aantal
        count = tr.select_one("td:nth-of-type(1)").get_text(strip=True)

        # Naam (via <span class="species-common-name">) of fallback op scientific-name
        common_el = tr.select_one(".species-common-name")
        scientific_el = tr.select_one(".species-scientific-name")
        common_name = (
            common_el.get_text(strip=True)
            if common_el
            else (scientific_el.get_text(strip=True) if scientific_el else None)
        )

        # Wetenschappelijke (Latijnse) naam
        latin_name = scientific_el.get_text(
            strip=True) if scientific_el else None

        # Plaats & waarnemer
        place = tr.select_one("td:nth-of-type(5) a").get_text(strip=True)
        observer = tr.select_one("td:nth-of-type(6) a").get_text(strip=True)

        # Foto-link (camera-icoon)
        photo_link = None
        pic_a = tr.select_one("td:last-of-type a")
        if pic_a and pic_a.get("href"):
            photo_link = BASE_URL + pic_a["href"]

        records.append({
            "count": count,
            "common_name": common_name,
            "latin_name": latin_name,
            "description": None,        # Vul later via wiki.py / OpenAI
            "place": place,
            "observer": observer,
            "photo_link": photo_link
        })

    return records
