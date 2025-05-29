# NatuurSpotter/naming.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def to_latin(common_name: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or not common_name:
        return "Unknown"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    prompt = (
        f"Geef enkel de Latijnse naam van de keversoort: “{common_name}”."
        " Zonder verdere uitleg."
    )
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        return text
    except Exception:
        return "Unknown"
