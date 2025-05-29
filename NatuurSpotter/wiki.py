# NatuurSpotter/wiki.py

import os
import requests
from bs4 import BeautifulSoup
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_description(common_name: str, latin_name: str) -> str:
    # kies Latijnse naam voor Wikipedia-URL, anders common name
    term = latin_name if latin_name and latin_name != "Unknown" else common_name
    url = "https://nl.wikipedia.org/wiki/" + term.replace(" ", "_")

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        para = soup.select_one("div.mw-parser-output > p")
        if not para:
            return "-"
        raw = para.get_text(strip=True)

        # vraag OpenAI om 2-zinnen samenvatting
        prompt = (
            f"Vat in twee zinnen samen (in het Nederlands):\n\n{raw}"
        )
        comp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        summ = comp.choices[0].message.content.strip()
        return summ or "-"
    except Exception:
        return "-"
