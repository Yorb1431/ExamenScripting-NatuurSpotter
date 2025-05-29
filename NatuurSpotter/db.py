# NatuurSpotter/db.py

import os
import pymysql.cursors

connection = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "natuurspotter"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)


def get_cached(date):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM daylist_cache WHERE obs_date = %s",
            (date,)
        )
        return cur.fetchall()


def cache_daylist(date, records):
    with connection.cursor() as cur:
        for r in records:
            cur.execute(
                """
                INSERT INTO daylist_cache
                  (obs_date, `count`, common_name, latin_name, place, observer, photo_link)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    date,
                    r["count"],
                    r["common_name"],
                    r["latin_name"],
                    r["place"],
                    r["observer"],
                    r["photo_link"],
                )
            )
        connection.commit()
