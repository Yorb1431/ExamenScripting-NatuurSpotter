# NatuurSpotter/db.py

import os
from dotenv import load_dotenv
import pymysql

# laad .env
load_dotenv()

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
        for rec in records:
            cursor.execute(
                """
                INSERT INTO daylist_cache
                  (obs_date, `count`, common_name, latin_name,
                   description, place, observer, photo_link)
                VALUES
                  (%s,       %s,      %s,          %s,
                   %s,            %s,    %s,        %s)
                """,
                (
                    obs_date,
                    rec["count"],
                    rec["common_name"],
                    rec["latin_name"],
                    rec["description"],
                    rec["place"],
                    rec["observer"],
                    rec["photo_link"],
                )
            )
        connection.commit()
