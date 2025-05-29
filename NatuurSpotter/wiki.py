# NatuurSpotter/wiki.py

import requests
from bs4 import BeautifulSoup


def scrape_wikipedia(common_name: str) -> dict:
    """
    Haal van nl.wikipedia.org de titel en eerste alinea op.
    Als pagina niet bestaat, return lege velden.
    """
    slug = common_name.replace(" ", "_")
    url = f"https://nl.wikipedia.org/wiki/{slug}"
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.HTTPError:
        return {"common": common_name, "description": ""}

    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("h1", id="firstHeading").get_text(strip=True)
    p = soup.select_one("#mw-content-text p")
    desc = p.get_text(strip=True) if p else ""
    return {"common": title, "description": desc}
