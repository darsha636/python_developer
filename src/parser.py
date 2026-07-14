import ast
import sqlite3
import os
from datetime import datetime

try:
    # Connect to SQLite database
    connection = sqlite3.connect("pychronicle.db")
    cursor = connection.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS variables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        file_name TEXT NOT NULL,
        line_number INTEGER NOT NULL,
        variable_name TEXT NOT NULL,
        serialized_value TEXT NOT NULL,
        data_type TEXT NOT NULL
    )
    """)
    connection.commit()

    # Clear previous records
    cursor.execute("DELETE FROM variables")
    connection.commit()

    # Read the Python file
    file_name = "sample_code/example.py"

    with open(file_name, "r") as file:
        code = file.read()

    # Convert Python code into AST
    tree = ast.parse(code)

    print("===== Variable Assignments =====\n")

    variable_count = 0

    # Find all variable assignments
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):

                    variable_name = target.id
                    line_number = node.lineno

                    if isinstance(node.value, ast.Constant):
                        value = str(node.value.value)
                        data_type = type(node.value.value).__name__
                    else:
                        value = "Unsupported"
                        data_type = "Unknown"

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Store data in database
                    cursor.execute("""
                    INSERT INTO variables
                    (timestamp, file_name, line_number,
                     variable_name, serialized_value, data_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        timestamp,
                        file_name,
                        line_number,
                        variable_name,
                        value,
                        data_type
                    ))

                    variable_count += 1

                    # Print output
                    print(f"File Name     : {file_name}")
                    print(f"Variable Name : {variable_name}")
                    print(f"Line Number   : {line_number}")
                    print(f"Value         : {value}")
                    print(f"Data Type     : {data_type}")
                    print("------------------------------")

    # Save all changes
    connection.commit()

    print("\n===== Summary =====")
    print(f"Total Variables : {variable_count}")
    print("Database        : pychronicle.db")
    print("Status          : Success")

except Exception as e:
    print("Error:", e)

finally:
    if 'connection' in locals():
        connection.close()