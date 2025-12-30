# db.py

import mysql.connector
from config import DB_CONFIG

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG.get("port", 3306),
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            autocommit=False
        )
        return conn

    except mysql.connector.Error as err:
        print("Database connection error:", err)
        raise
