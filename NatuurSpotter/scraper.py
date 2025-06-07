# NatuurSpotter/scraper.py
# Web scrapingvoor NatuurSpotter

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from NatuurSpotter.wiki import scrape_wikipedia


def get_image_from_wiki(common_name: str) -> str:
    # Probee eerst Nederlandse Wikipedia, valt terug op een standaard afbeelding
    try:
        url = f"https://nl.wikipedia.org/wiki/{common_name.replace(' ', '_')}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        infobox = soup.select_one("table.infobox")
        if infobox:
            img = infobox.select_one("img")
            if img and img.get("src"):
                return f"https:{img['src']}" if img['src'].startswith("//") else img['src']

        img = soup.select_one("div#mw-content-text img")
        if img and img.get("src"):
            return f"https:{img['src']}" if img['src'].startswith("//") else img['src']

    except Exception:
        pass

    return "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Beetle_icon.svg/1200px-Beetle_icon.svg.png"


def scrape_daylist(date: str, species_group: int, country_division: str = ""):
    # Haalt een daglijst op van waarnemingen.be
    # Geeft een lijst terug met waarnemingen inclusief:
    # - Nederlandse naam
    # - Aantal
    # - Datum
    # - Locatie
    # - Waarnemer
    # - Foto link
    # - Beschrijving
    url = (
        f"https://waarnemingen.be/fieldwork/observations/daylist/"
        f"?date={date}&species_group={species_group}&country_division={country_division}&rarity=&search=&page=1"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[scraper] Fout bij ophalen van {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if table is None:
        return []

    results = []
    for tr in table.select("tbody > tr"):
        tds = tr.find_all("td")
        if not tds or len(tds) < 6:
            continue

        name_tag = tr.select_one("td:nth-of-type(4) a")
        common_name = name_tag.get_text(strip=True) if name_tag else ""

        count_tag = tr.select_one("td:nth-of-type(2)")
        count = count_tag.get_text(strip=True) if count_tag else ""

        place_tag = tr.select_one("td:nth-of-type(5) a")
        place = place_tag.get_text(strip=True) if place_tag else ""

        observer_tag = tr.select_one("td:nth-of-type(6) a")
        observer = observer_tag.get_text(strip=True) if observer_tag else ""

        # coördinaten
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

        # oto link
        photo_link = None
        photo_td = tr.select_one("td:last-of-type a")
        if photo_td and photo_td.get("href"):
            photo_link = photo_td["href"]
            if photo_link.startswith("/"):
                photo_link = f"https://waarnemingen.be{photo_link}"

        #  beschrijving Wikipedia
        wiki_info = scrape_wikipedia(common_name)
        description = wiki_info.get(
            "description", f"Information about {common_name}")

        if not photo_link:
            photo_link = get_image_from_wiki(common_name)

        results.append({
            "common_name": common_name,
            "count": count,
            "date": date,
            "place": place,
            "observer": observer,
            "lat": lat,
            "lon": lon,
            "photo_link": photo_link,
            "description": description,
        })

    return results


def scrape_all_observations(date):
    if isinstance(date, datetime):
        date_str = date.strftime('%Y-%m-%d')
    else:
        date_str = str(date)
    url = f"https://waarnemingen.be/fieldwork/observations/daylist/?date={date_str}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if not table:
        return []
    rows = table.find_all('tr')[1:]  # geen head
    observations = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue
        species = cols[3].get_text(strip=True)
        location = cols[4].get_text(strip=True)
        observer = cols[5].get_text(strip=True) if len(cols) > 5 else ''
        count = cols[1].get_text(strip=True)
        observations.append({
            'species': species,
            'location': location,
            'observer': observer,
            'count': count,
            'date': date_str
        })
    return observations
