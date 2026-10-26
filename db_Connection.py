import os
import psycopg2

def get_db_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# Example query
cursor.execute("SHOW TABLES;")

# Print all tables
for table in cursor.fetchall():
    print(table)

# Close cursor and connection
cursor.close()
conn.close()
