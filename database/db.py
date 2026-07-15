import sqlite3

connection = sqlite3.connect("pychronicle.db")
cursor = connection.cursor()

# Delete old table if it exists (for development only)
cursor.execute("DROP TABLE IF EXISTS variables")

# Create new table
cursor.execute("""
CREATE TABLE variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    file_name TEXT,
    line_number INTEGER,
    variable_name TEXT,
    serialized_value TEXT,
    data_type TEXT
)
""")

connection.commit()
connection.close()

print("Database and table created successfully!")