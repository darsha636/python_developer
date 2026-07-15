import sqlite3

# Connect to the database (creates it if it doesn't exist)
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "pychronicle.db")
connection = sqlite3.connect(DB_PATH)

cursor = connection.cursor()

# Create the variables table
cursor.execute("""
CREATE TABLE IF NOT EXISTS variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    line_number INTEGER,
    variable_name TEXT,
    serialized_value TEXT
)
""")

connection.commit()

print("Database and table created successfully!")

connection.close()