# NatuurSpotter/scraper.py

import random


def scrape_daylist(date):
    # Simuleer scraping voor testdoeleinden
    dummy = [
        {
            "count": random.randint(1, 10),
            "common_name": "Lieveheersbeestje",
            "place": "Bergen",
            "observer": "J. Doe",
            "description": "Zat op een bloem.",
            "lat": 50.456,
            "lon": 3.948
        },
        {
            "count": random.randint(1, 10),
            "common_name": "Meikever",
            "place": "Henegouwen",
            "observer": "A. Example",
            "description": "In het gras.",
            "lat": 50.467,
            "lon": 3.976
        }
    ]
    return dummy
