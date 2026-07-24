import sqlite3
import datetime
import json

# Internal step counter for chronological ordering
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
        conn = sqlite3.connect("pychronicle.db")
        
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
    timestamp = datetime.datetime.now().isoformat()
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

def get_state_at(conn, step):
    """
    Returns the latest value of every distinct variable as of the given step.
    Useful for presenting a consolidated snapshot of the program state.
    """
    cursor = conn.cursor()
    query = """
        SELECT t1.*
        FROM trace_events t1
        INNER JOIN (
            SELECT variable_name, MAX(step) as max_step
            FROM trace_events
            WHERE step <= ?
            GROUP BY variable_name
        ) t2 ON t1.variable_name = t2.variable_name AND t1.step = t2.max_step
        ORDER BY t1.variable_name ASC
    """
    cursor.execute(query, (step,))
    return cursor.fetchall()
