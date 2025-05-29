# NatuurSpotter/wiki.py

import requests
from bs4 import BeautifulSoup


def scrape_wikipedia(common_name: str) -> dict:
    """
    Probeer eerst de Nederlandstalige Wikipedia-pagina, 
    en val zonodig terug op Engels.
    Haal de eerste alinea als ruwe beschrijving.
    """
    slug = common_name.replace(" ", "_")
    urls = [
        f"https://nl.wikipedia.org/wiki/{slug}",
        f"https://en.wikipedia.org/wiki/{slug}"
    ]
    description = ""
    for url in urls:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            # eerste <p> in content
            p = soup.select_one("div#mw-content-text p")
            if p:
                text = p.get_text(strip=True)
                if text:
                    description = text
                    break
        except Exception:
            # 404 of parse‐fout → volgende URL
            continue
    # crop op max. 255 chars
    if len(description) > 255:
        description = description[:252].rsplit(" ", 1)[0] + "..."
    return {"description": description}
