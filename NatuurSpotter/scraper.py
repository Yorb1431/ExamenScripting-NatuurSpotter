# NatuurSpotter/scraper.py

import requests
from bs4 import BeautifulSoup

BASE = "https://waarnemingen.be"


def scrape_daylist(date, species_group, country_division):
    url = (
        f"{BASE}/fieldwork/observations/daylist/"
        f"?date={date}"
        f"&species_group={species_group}"
        f"&country_division={country_division}"
        f"&rarity=&search="
    )
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = soup.select("table tbody tr")
    results = []
    for tr in rows:
        # aantal
        count = tr.select_one("td.text-right").get_text(strip=True)
        # soorten-cel
        cell = tr.select_one("td.column-species")
        common_span = cell.select_one("span.species-common-name")
        sci_i = cell.select_one("i.species-scientific-name")
        if common_span:
            common_name = common_span.get_text(strip=True)
        else:
            common_name = sci_i.get_text(strip=True)

        # plaats + waarnemer
        place = tr.select("td")[4].get_text(strip=True)
        observer = tr.select("td")[5].get_text(strip=True)

        # fotolink
        photo_a = tr.select_one("td a[href*='/photos/']")
        photo_link = BASE + photo_a["href"] if photo_a else None

        results.append({
            "count": count,
            "common_name": common_name,
            "place": place,
            "observer": observer,
            "photo_link": photo_link
        })

    return results
