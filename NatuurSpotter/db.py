# NatuurSpotter/db.py

import os
import pymysql
from pathlib import Path

# **1) Zelf .env inlezen (omdat je python-dotenv niet wilt gebruiken)**
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('\'"')
        # zet alleen als niet al bestaan
        os.environ.setdefault(key, val)

# **2) Maak database-connectie**
connection = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "natuurspotter"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)


def get_cached(obs_date):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM daylist_cache WHERE obs_date = %s",
            (obs_date,)
        )
        return cursor.fetchall()


def cache_daylist(obs_date, records):
    with connection.cursor() as cursor:
        for r in records:
            cursor.execute("""
                INSERT INTO daylist_cache
                    (obs_date, `count`, common_name, latin_name, place, observer, photo_link, description)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                           (
                               obs_date,
                               r.get("count"),
                               r.get("common_name"),
                               r.get("latin_name"),
                               r.get("place"),
                               r.get("observer"),
                               r.get("photo_link"),
                               r.get("description"),
                           )
                           )
        connection.commit()


def get_species_info(common_name):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM species_info WHERE common_name = %s",
            (common_name,)
        )
        return cursor.fetchone()


def save_species_info(common_name, latin_name, description):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO species_info (common_name, latin_name, description)
            VALUES (%s, %s, %s)
            """,
                       (common_name, latin_name, description)
                       )
        connection.commit()


def update_description(obs_date, common_name, description):
    """
    Werk de kolom `description` bij in daylist_cache voor één record.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE daylist_cache
               SET description = %s
             WHERE obs_date = %s
               AND common_name = %s
            """,
                       (description, obs_date, common_name)
                       )
    connection.commit()


def get_recent_observations(limit=10):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM daylist_cache ORDER BY obs_date DESC LIMIT %s", (limit,))
        return cursor.fetchall()
