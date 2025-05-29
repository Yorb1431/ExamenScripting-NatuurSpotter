import os
import pymysql

# Laadt .env-variabelen als je python-dotenv hebt geïnstalleerd
from dotenv import load_dotenv
load_dotenv()

connection = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "natuurspotter"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)


def get_cached(date):
    """Haalt alle records voor één datum uit de cache."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM daylist_cache WHERE obs_date = %s",
            (date,)
        )
        return cursor.fetchall()


def cache_daylist(date, records):
    """Slaat een set opgehaalde waarnemingen in de cache."""
    with connection.cursor() as cursor:
        for r in records:
            cursor.execute(
                """
                INSERT INTO daylist_cache
                  (obs_date, `count`, common_name, latin_name, description,
                   place, observer, photo_link, lat, lon)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    date,
                    r["count"],
                    r["common_name"],
                    r["latin_name"],
                    None,                   # description wordt later ingevuld
                    r["place"],
                    r["observer"],
                    r.get("photo_link"),
                    r.get("lat"),
                    r.get("lon"),
                )
            )
        connection.commit()


def update_description(record_id, description):
    """Werk de description-kolom bij voor één record."""
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE daylist_cache SET description = %s WHERE id = %s",
            (description, record_id)
        )
        connection.commit()
