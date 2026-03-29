# =============================================
# db.py — Database Connection
# This file handles all MySQL connections
# =============================================

import mysql.connector    # Library to talk to MySQL
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env credentials

def get_connection():
    """
    Creates and returns a MySQL database connection.
    Call this function whenever you need to query the database.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),        # Usually 'localhost'
            user=os.getenv("DB_USER"),        # Usually 'root'
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")     # 'chuk_chatbot'
        )
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Database connection failed: {e}")
        return None


def execute_query(query, params=None, fetch=False):
    """
    Helper function to run any SQL query.

    query  = the SQL command (string)
    params = values to insert safely (tuple) — prevents SQL injection
    fetch  = True if you want to GET data back, False if just saving data
    """
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)  # dictionary=True returns rows as {column: value}

    try:
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()   # Get all matching rows
            return result
        else:
            conn.commit()                # Save changes to database
            return cursor.lastrowid      # Return ID of last inserted row

    except mysql.connector.Error as e:
        print(f"❌ Query failed: {e}")
        return None

    finally:
        cursor.close()
        conn.close()                     # Always close connection when done