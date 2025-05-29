# NatuurSpotter/wiki.py

import os
import requests
from dotenv import load_dotenv

# Laadt je .env zodat OPENROUTER_API_KEY beschikbaar is
load_dotenv()


def generate_description(latin_name: str) -> str:
    """
    Vraagt via OpenRouter (GPT-3.5-turbo) om een bondige beschrijving
    (maximaal twee zinnen, 255 karakters) van de keversoort.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or not latin_name:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # Optioneel, net als in naming.py
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "NatuurSpotter"
    }

    prompt = (
        f"Geef een bondige beschrijving in maximaal twee zinnen "
        f"(maximaal 255 karakters) van de keversoort '{latin_name}'."
    )

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        resp.raise_for_status()
        content = resp.json()
        text = content["choices"][0]["message"]["content"].strip()
        # Zorg dat we niet over de limiet van 255 karakters heen gaan
        return text[:255]
    except Exception as e:
        # Log eventuele fouten (in dev-mode zie je ze in de console)
        print("❌ Error generate_description:", e)
        return None
