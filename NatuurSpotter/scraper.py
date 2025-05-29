import requests
from bs4 import BeautifulSoup


def fetch_data(date):
    url = f"https://waarnemingen.be/observations/daylist/?datum={date}&groep=7&soort=0&provincie=0&locatie=0"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    observations = []

    for row in soup.select("tr[class*=ObservationRow]"):
        columns = row.select("td")

        if len(columns) < 6:
            continue

        try:
            species = columns[0].select_one("a")
            observer = columns[1].get_text(strip=True)
            location = columns[2].get_text(strip=True)
            count = columns[3].get_text(strip=True)
            details = columns[5].get_text(strip=True)

            latin = species["data-original-title"].strip(
            ) if "data-original-title" in species.attrs else ""
            common = species.get_text(strip=True)

            if common.lower() == latin.lower() or not common:
                common = None

            observations.append({
                "common_name": common or latin,
                "latin_name": latin,
                "observer": observer,
                "place": location,
                "count": count,
                "description": details
            })
        except Exception:
            continue

    return observations
