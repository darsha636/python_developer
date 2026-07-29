import ast
import sqlite3
import os
import sys
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python parser.py <target_file.py>")
        sys.exit(1)

    target_file = sys.argv[1]

    if not os.path.exists(target_file):
        print(f"Error: File '{target_file}' not found.")
        sys.exit(1)

try:
    # Connect to SQLite database
    connection = sqlite3.connect("pychronicle.db")
    cursor = connection.cursor()

    # Design a fast SQLite schema
    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS variables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        line_number INTEGER NOT NULL,
        variable_name TEXT NOT NULL,
        serialized_value TEXT NOT NULL
    )
    """)
    
    # Create indexes for fast querying based on common access patterns
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON variables (timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_line_number ON variables (line_number)")

    # Read the Python file
    with open(target_file, "r", encoding="utf-8") as file:
        code = file.read()

    # Convert Python code into AST
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"Syntax error in target file at line {e.lineno}: {e.msg}")
        sys.exit(1)

    print(f"Parsing AST for '{target_file}'...\n")
    print(f"{'Line':<6} | {'Variable':<20} | {'Expression/Value'}")
    print("-" * 60)
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
                    
                    # ast.unparse converts the AST node back to a readable code string
                    # This captures lists, dicts, function calls, etc. not just simple Constants.
                    try:
                        serialized_value = ast.unparse(node.value)
                    except Exception:
                        serialized_value = "Unsupported"

                    # Current timestamp in ISO format
                    timestamp = datetime.now().isoformat()

                    # Save data into SQLite database
                    cursor.execute("""
                    INSERT INTO variables
                    (timestamp, line_number, variable_name, serialized_value)
                    VALUES (?, ?, ?, ?)
                    """, (timestamp, line_number, variable_name, serialized_value))

                    # Print output
                    print(f"{line_number:<6} | {variable_name:<20} | {serialized_value}")

    # Save all changes
    connection.commit()
    
    # Close the database
    connection.close()
    
    print("\nAll variable assignments saved successfully to pychronicle.db!")

if __name__ == "__main__":
    main()

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
