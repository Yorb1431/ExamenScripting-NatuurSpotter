import os
import requests
from dotenv import load_dotenv

load_dotenv()


def to_latin(common_name):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or not common_name:
        return "Onbekend"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "NatuurSpotter"
    }

    prompt = f"Wat is de Latijnse naam van deze keversoort: '{common_name}'? Geef enkel de Latijnse naam zonder uitleg."

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Fout bij ophalen Latijnse naam: {e}")
        return "Onbekend"


def to_common(latin_name):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or not latin_name:
        return "Onbekend"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "NatuurSpotter"
    }

    prompt = f"Wat is de Nederlandse naam van deze Latijnse keversoort: '{latin_name}'? Geef enkel de naam, zonder uitleg."

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Fout bij ophalen gewone naam: {e}")
        return "Onbekend"
