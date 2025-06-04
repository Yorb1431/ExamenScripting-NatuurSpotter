# NatuurSpotter/wiki.py

import requests
from bs4 import BeautifulSoup
import re

def clean_text(text: str) -> str:
    """Clean and format the text, removing extra spaces and newlines."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_first_paragraph(soup: BeautifulSoup) -> str:
    """Try to get the first meaningful paragraph from the Wikipedia page."""
    # Try different selectors to find the first paragraph
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
            # Skip paragraphs that are too short or contain mostly links
            if text and len(text) > 20 and not text.startswith("Wikimedia Commons"):
                return text
    return ""

def get_taxonomy_info(soup: BeautifulSoup) -> str:
    """Try to get taxonomy information from the infobox."""
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
    """Get a comprehensive description by combining different sources."""
    description_parts = []
    
    # Get first paragraph
    first_para = get_first_paragraph(soup)
    if first_para:
        description_parts.append(first_para)
    
    # Get taxonomy info
    taxonomy = get_taxonomy_info(soup)
    if taxonomy:
        description_parts.append(f"Taxonomy: {taxonomy}")
    
    # If we have no description yet, try to get any meaningful content
    if not description_parts:
        content = soup.select_one("div#mw-content-text")
        if content:
            text = clean_text(content.get_text())
            if text and len(text) > 50:
                description_parts.append(text[:500] + "...")
    
    # If still no description, create a basic one
    if not description_parts:
        description_parts.append(f"{common_name} is a beetle species found in the Hainaut region of Belgium. It belongs to the Coleoptera order of insects.")
    
    return " ".join(description_parts)

def scrape_wikipedia(common_name: str) -> dict:
    """
    Try to get a description from Wikipedia, with multiple fallback options.
    Returns a dictionary with a description that's always populated.
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
            
            # Get comprehensive description
            description = get_species_description(soup, common_name)
            
            # If we found something meaningful, break the loop
            if description and len(description) > 50:
                break
                
        except Exception:
            continue
    
    # If still no description, create a basic one
    if not description or len(description) < 50:
        description = f"{common_name} is a beetle species found in the Hainaut region of Belgium. It belongs to the Coleoptera order of insects, which is the largest order of insects with over 400,000 described species."
    
    # Ensure the description is not too long
    if len(description) > 500:
        description = description[:497].rsplit(" ", 1)[0] + "..."
    
    return {"description": description}
