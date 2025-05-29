import pymysql
import os
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
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM daylist_cache WHERE obs_date = %s", (date,))
        return cursor.fetchall()


def cache_daylist(date, records):
    with connection.cursor() as cursor:
        for record in records:
            cursor.execute(
                """
                INSERT INTO daylist_cache 
                (obs_date, count, common_name, place, observer, description, lat, lon) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    date,
                    record["count"],
                    record["common_name"],
                    record["place"],
                    record["observer"],
                    record["description"],
                    record.get("lat"),
                    record.get("lon"),
                )
            )
        connection.commit()


def get_species_info(common_name):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM species_info WHERE common_name = %s", (common_name,))
        return cursor.fetchone()


def save_species_info(common_name, latin_name, description):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO species_info (common_name, latin_name, description)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE latin_name=VALUES(latin_name), description=VALUES(description)
                """,
                (common_name, latin_name, description)
            )
            connection.commit()
        except Exception as e:
            print("Database insert error:", e)
