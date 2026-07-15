import sqlite3

# Connect to the database
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "pychronicle.db")
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Count total records
cursor.execute("SELECT COUNT(*) FROM variables")
total_variables = cursor.fetchone()[0]

# Count unique variable names
cursor.execute("SELECT COUNT(DISTINCT variable_name) FROM variables")
unique_variables = cursor.fetchone()[0]

print("\n===== Database Summary =====")
print(f"Total Variables      : {total_variables}")
print(f"Unique Variable Names: {unique_variables}")

connection.close()