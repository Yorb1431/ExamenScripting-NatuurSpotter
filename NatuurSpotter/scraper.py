# NatuurSpotter/scraper.py

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://waarnemingen.be"


def scrape_daylist(date, species_group, country_division):
    """
    Scrape de daylist-pagina voor Coleoptera:
    - date: "YYYY-MM-DD"
    - species_group: int (16 voor Coleoptera)
    - country_division: int (23 voor Henegouwen)
    Retourneert een lijst dicts met keys:
      count, common_name, latin_name, place, observer, photo_link
    """
    url = f"{BASE_URL}/fieldwork/observations/daylist/"
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
        # Aantal
        count = cols[0].get_text(strip=True)

        # Soortnamen: probeer eerst common_name, anders haal alleen scientific-name
        common_tag = cols[3].select_one(".species-common-name")
        sci_tag = cols[3].select_one(".species-scientific-name")
        if common_tag:
            common_name = common_tag.get_text(strip=True)
        else:
            # fallback: gebruik de wetenschappelijke naam
            common_name = sci_tag.get_text(
                strip=True) if sci_tag else cols[3].get_text(strip=True)

        latin_name = sci_tag.get_text(strip=True) if sci_tag else ""

        # Plaats & waarnemer
        place = cols[4].get_text(strip=True)
        observer = cols[5].get_text(strip=True)

        # Foto‐link (eerste <a> in kolom 6)
        photo_link = None
        a = cols[6].find("a", href=True)
        if a:
            href = a["href"]
            # volledige URL
            photo_link = href if href.startswith("http") else BASE_URL + href

        out.append({
            "count":       count,
            "common_name": common_name,
            "latin_name":  latin_name,
            "place":       place,
            "observer":    observer,
            "photo_link":  photo_link,
            "date":        date
        })

    return out
