import os
import requests


def to_latin(common_name):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or not common_name:
        return "Unknown"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"Geef alleen de Latijnse naam voor deze keversoort: '{common_name}'."
    )
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return "Unknown"
