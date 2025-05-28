# NatuurSpotter/naming.py

import os
import requests


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

    prompt = f"Geef de Latijnse naam voor deze keversoort: '{common_name}'. Geef alleen de naam, zonder uitleg."

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        content = response.json()
        return content["choices"][0]["message"]["content"].strip()
    except Exception:
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

    prompt = f"Wat is de algemene Nederlandse naam voor de kever met Latijnse naam '{latin_name}'? Geef enkel de gewone naam zonder uitleg."

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        content = response.json()
        return content["choices"][0]["message"]["content"].strip()
    except Exception:
        return "Onbekend"
