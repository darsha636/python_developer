import sqlite3
import json
from datetime import datetime


DATABASE = "pychronicle.db"


def store_compressed_delta(compressed_delta, line_number=0):
    """
    Store compressed delta data in the variables table.
    """

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

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