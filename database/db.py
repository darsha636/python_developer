import sqlite3

# Connect to the database (creates it if it doesn't exist)
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "pychronicle.db")
connection = sqlite3.connect(DB_PATH)

connection = sqlite3.connect("pychronicle.db")
cursor = connection.cursor()

# Delete old table if it exists (for development only)
cursor.execute("DROP TABLE IF EXISTS variables")

# Create new table
cursor.execute("""
CREATE TABLE IF NOT EXISTS variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    file_name TEXT,
    line_number INTEGER,
    variable_name TEXT,
    serialized_value TEXT,
    data_type TEXT
)
""")
# Add compressed delta column if it does not already exist
cursor.execute("PRAGMA table_info(variables)")
columns = [column[1] for column in cursor.fetchall()]

if "compressed_delta" not in columns:
    cursor.execute("""
        ALTER TABLE variables
        ADD COLUMN compressed_delta BLOB
    """)

    print("compressed_delta column added successfully.")
else:
    print("compressed_delta column already exists.")
connection.commit()
connection.close()

print("Database setup completed successfully!")