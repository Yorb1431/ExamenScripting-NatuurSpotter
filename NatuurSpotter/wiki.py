# NatuurSpotter/wiki.py
# Wikipedia scraping functionaliteit voor NatuurSpotter

import requests
from bs4 import BeautifulSoup
import re


def clean_text(text: str) -> str:
    # Maakt tekst  door extra spaties / regels te verwijderen
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_first_paragraph(soup: BeautifulSoup) -> str:
    selectors = [
        "div#mw-content-text p:not(.mw-empty-elt)",
        "div#mw-content-text p",
        "div.mw-parser-output p:not(.mw-empty-elt)",
        "div.mw-parser-output p"
    ]

    for selector in selectors:
        paragraphs = soup.select(selector)
        for p in paragraphs:
            text = clean_text(p.get_text())
            if text and len(text) > 20 and not text.startswith("Wikimedia Commons"):
                return text
    return ""


def get_taxonomy_info(soup: BeautifulSoup) -> str:
    # Haalt taxonomische informatie op uit de infobox
    infobox = soup.select_one("table.infobox")
    if infobox:
        rows = infobox.select("tr")
        taxonomy_info = []
        for row in rows:
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td:
                label = clean_text(th.get_text())
                value = clean_text(td.get_text())
                if label and value and not label.startswith("Afbeelding"):
                    taxonomy_info.append(f"{label}: {value}")
        if taxonomy_info:
            return " | ".join(taxonomy_info)
    return ""


def get_species_description(soup: BeautifulSoup, common_name: str) -> str:
    description_parts = []

    #  eerste paragraaf
    first_para = get_first_paragraph(soup)
    if first_para:
        description_parts.append(first_para)

    taxonomy = get_taxonomy_info(soup)
    if taxonomy:
        description_parts.append(f"Taxonomy: {taxonomy}")

    if not description_parts:
        content = soup.select_one("div#mw-content-text")
        if content:
            text = clean_text(content.get_text())
            if text and len(text) > 50:
                description_parts.append(text[:500] + "...")

    #  geen beschrijving / maak een basisbeschrijvingAPI
    if not description_parts:
        description_parts.append(
            f"{common_name} is een kever soort gevonden in de regio Henegouwen in België. Het behoort tot de orde Coleoptera van insecten.")

    return " ".join(description_parts)


def scrape_wikipedia(common_name: str) -> dict:
    # Geeft dictionary  met  beschrijving
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

            description = get_species_description(soup, common_name)

            if description and len(description) > 50:
                break

        except Exception:
            continue

    if not description or len(description) < 50:
        description = f"{common_name} is een kever soort gevonden in de regio Henegouwen in België. Het behoort tot de orde Coleoptera van insecten, wat de grootste orde van insecten is met meer dan 400.000 beschreven soorten."

    if len(description) > 500:
        description = description[:497].rsplit(" ", 1)[0] + "..."

    return {"description": description}
