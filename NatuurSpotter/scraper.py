# NatuurSpotter/scraper.py

import requests
from bs4 import BeautifulSoup


def scrape_daylist(date: str, species_group: int, country_division: int):
    """
    Scrape een daglijst (bijv. van waarnemingen.be) voor de opgegeven datum,
    species_group en country_division. Geeft een lijst terug van dicts met keys:
    - common_name (str)
    - count       (str)
    - date        (str)
    - place       (str)
    - observer    (str)
    - lat         (float of None)
    - lon         (float of None)
    """
    # Pas de URL aan naar de echte bron; dit is een voorbeeldstructuur.
    url = (
        f"https://waarnemingen.be/rbc?"
        f"acc={species_group}&gebied={country_division}&datum={date}"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[scraper] Fout bij ophalen van {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    # Vind de tabel (pas class/id aan op basis van werkelijke HTML)
    table = soup.find("table", {"class": "waarnemingen-tabel"})
    if table is None:
        # Geen waarnemingen-tabel gevonden → lege lijst
        return []

    results = []
    # Itereer over elke rij in <tbody>; header-rij(en) negeren
    for tr in table.select("tbody > tr"):
        tds = tr.find_all("td")
        if not tds or len(tds) < 6:
            # Te weinig kolommen, sla over
            continue

        # ==== common_name ====
        name_tag = tr.select_one("td:nth-of-type(3) a")
        common_name = name_tag.get_text(strip=True) if name_tag else ""

        # ==== count ====
        count_tag = tr.select_one("td:nth-of-type(4)")
        count = count_tag.get_text(strip=True) if count_tag else ""

        # ==== place ====
        place_tag = tr.select_one("td:nth-of-type(5) a")
        place = place_tag.get_text(strip=True) if place_tag else ""

        # ==== observer ====
        observer_tag = tr.select_one("td:nth-of-type(6) a")
        observer = observer_tag.get_text(strip=True) if observer_tag else ""

        # ==== lat / lon (bijvoorbeeld in data-lat / data-lon attributes) ====
        lat, lon = None, None
        if place_tag:
            lat_attr = place_tag.get("data-lat")
            lon_attr = place_tag.get("data-lon")
            try:
                lat = float(lat_attr) if lat_attr else None
                lon = float(lon_attr) if lon_attr else None
            except ValueError:
                lat = None
                lon = None

        results.append({
            "common_name": common_name,
            "count": count,
            "date": date,
            "place": place,
            "observer": observer,
            "lat": lat,
            "lon": lon,
        })

    return results
