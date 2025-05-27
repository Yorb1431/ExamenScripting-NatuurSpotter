# main.py

import os
import mysql.connector


def load_env_file(env_path=".env"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    full_path = os.path.join(project_root, env_path)
    try:
        with open(full_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                os.environ[key] = val
    except FileNotFoundError:
        raise RuntimeError(f".env bestand niet gevonden op: {full_path}")


# laad .env uit root
load_env_file()

# DB-connectie
connection = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME")
)

print("Verbonden met de database")
print(f"Database:      {connection.database}")

# sluit de verbinding
connection.close()
print("Verbinding gesloten")
