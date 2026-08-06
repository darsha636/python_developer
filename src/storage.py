import sqlite3
import json
import datetime
from datetime import datetime as dt

DATABASE = "pychronicle.db"
_step_counter = 0

def create_connection(in_memory=True):
    """
    Creates a SQLite connection and initializes the schema.
    """
    global _step_counter
    _step_counter = 0
    
    if in_memory:
        conn = sqlite3.connect(":memory:")
    else:
        conn = sqlite3.connect(DATABASE)
        
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trace_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step INTEGER,
            timestamp TEXT,
            line_number INTEGER,
            function_name TEXT,
            variable_name TEXT,
            variable_value TEXT,
            value_type TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS variables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            line_number INTEGER,
            variable_name TEXT,
            serialized_value TEXT,
            compressed_delta BLOB
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_step ON trace_events (step)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_line_number ON trace_events (line_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_variable_name ON trace_events (variable_name)")
    
    conn.commit()
    return conn

def record_event(conn, line_number, variable_name, value, function_name="<module>"):
    """
    Records a variable mutation event into the trace database.
    """
    global _step_counter
    _step_counter += 1
    
    cursor = conn.cursor()
    # Serialize the value safely as JSON
    try:
        val_repr = json.dumps(value)
    except TypeError:
        val_repr = json.dumps(str(value))

    val_type = type(value).__name__
    timestamp = dt.now().isoformat()
    cursor.execute("""
        INSERT INTO trace_events (step, timestamp, line_number, function_name, variable_name, variable_value, value_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (_step_counter, timestamp, line_number, function_name, variable_name, val_repr, val_type))
    
    conn.commit()

def get_all_events(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trace_events ORDER BY step ASC")
    return cursor.fetchall()

def get_events_up_to_step(conn, step):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trace_events WHERE step <= ? ORDER BY step ASC", (step,))
    return cursor.fetchall()

def get_history_for_variable(conn, name):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trace_events WHERE variable_name = ? ORDER BY step ASC", (name,))
    return cursor.fetchall()

def get_events_at_line(conn, line):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trace_events WHERE line_number = ? ORDER BY step ASC", (line,))
    return cursor.fetchall()

def count_events(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM trace_events")
    return cursor.fetchone()[0]

def store_compressed_delta(compressed_delta, line_number=0):
    """
    Store compressed delta data in the variables table.
    """
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    timestamp = dt.now().isoformat()

    cursor.execute(
        """
        INSERT INTO variables
        (timestamp, line_number, variable_name, serialized_value, compressed_delta)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            line_number,
            "execution_state",
            json.dumps({}),
            compressed_delta
        )
    )

    connection.commit()
    record_id = cursor.lastrowid

    connection.close()

    return record_id

def retrieve_compressed_delta(record_id):
    """
    Retrieve compressed delta data from SQLite.
    """
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT compressed_delta
        FROM variables
        WHERE id = ?
        """,
        (record_id,)
    )

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None

    return result[0]

if __name__ == "__main__":
    print("SQLite storage module ready.")