# NatuurSpotter/scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from NatuurSpotter.wiki import scrape_wikipedia


def get_image_from_wiki(common_name: str) -> str:
    """Get an image URL from Wikipedia for the given species."""
    try:
        # Try Dutch Wikipedia first
        url = f"https://nl.wikipedia.org/wiki/{common_name.replace(' ', '_')}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Look for the first image in the infobox
        infobox = soup.select_one("table.infobox")
        if infobox:
            img = infobox.select_one("img")
            if img and img.get("src"):
                return f"https:{img['src']}" if img['src'].startswith("//") else img['src']
        
        # If no image in infobox, try the first image in the content
        img = soup.select_one("div#mw-content-text img")
        if img and img.get("src"):
            return f"https:{img['src']}" if img['src'].startswith("//") else img['src']
            
    except Exception:
        pass
    
    # If no image found, return a default beetle image
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Beetle_icon.svg/1200px-Beetle_icon.svg.png"

def scrape_daylist(date: str, species_group: int, country_division: str = ""):
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
    # Gebruik de juiste URL-structuur voor waarnemingen.be
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
    # Gebruik de eerste tabel op de pagina (de daglijst-tabel)
    table = soup.find("table")
    if table is None:
        # Geen tabel gevonden → lege lijst
        return []

    results = []
    # Itereer over elke rij in <tbody>; header-rij(en) negeren
    for tr in table.select("tbody > tr"):
        tds = tr.find_all("td")
        if not tds or len(tds) < 6:
            # Te weinig kolommen, sla over
            continue

        # ==== common_name ====
        name_tag = tr.select_one("td:nth-of-type(4) a")
        common_name = name_tag.get_text(strip=True) if name_tag else ""

        # ==== count ====
        count_tag = tr.select_one("td:nth-of-type(2)")
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

        # ==== photo_link (if present) ====
        photo_link = None
        # Usually the last <td> contains a link with a camera icon if a photo is present
        photo_td = tr.select_one("td:last-of-type a")
        if photo_td and photo_td.get("href"):
            photo_link = photo_td["href"]
            # Make absolute if needed
            if photo_link.startswith("/"):
                photo_link = f"https://waarnemingen.be{photo_link}"

        # Get description from Wikipedia
        wiki_info = scrape_wikipedia(common_name)
        description = wiki_info.get("description", f"Information about {common_name}")

        # Get image from Wikipedia if no photo_link
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
    """
    Scrape all observations for a given date from waarnemingen.be daylist.
    Returns a list of dicts: [{species, location, observer, count, ...}, ...]
    """
    # Format date as YYYY-MM-DD
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
    rows = table.find_all('tr')[1:]  # skip header
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
