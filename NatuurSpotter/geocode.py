import requests


def geocode_place(place):
    if not place:
        return None, None
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{place}, Belgium",
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "NatuurSpotter/1.0"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None
