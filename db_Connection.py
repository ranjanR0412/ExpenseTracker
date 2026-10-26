import mysql.connector
import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# def get_db_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Rohit@123",   # your actual password
#         database="expensetracker"
#     )

# # Create a single connection
# conn = get_db_connection()
# cursor = conn.cursor()

# Example query
cursor.execute("SHOW TABLES;")

# Print all tables
for table in cursor.fetchall():
    print(table)

# Close cursor and connection
cursor.close()
conn.close()
