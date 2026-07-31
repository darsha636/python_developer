"""
data_source.py
==============
Data-access layer for the PyChronicle Time-Scrubbing UI.

This module is the **only** place that knows about `storage.py`.
The TUI (tui_app.py) calls these functions exclusively, which makes
it trivial to:
  - Swap in the real SQLite backend (already done below via storage.py)
  - Mock/stub the layer for unit tests
  - Extend with a network backend later

Public API
----------
  get_total_steps(conn)                 -> int
  get_variables_for_step(conn, step)    -> dict[str, str]
  get_line_for_step(conn, step)         -> int
  get_function_for_step(conn, step)     -> str
  get_timestamp_for_step(conn, step)    -> str
  get_changed_vars_at_step(conn, step)  -> set[str]
  get_source_lines(file_path)           -> list[str]
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

# ---------------------------------------------------------------------------
# Internal helpers — query the trace_events table produced by storage.py
# ---------------------------------------------------------------------------

def _query_state_at(conn: sqlite3.Connection, step: int) -> list[tuple]:
    """
    Returns the latest value for every variable known up-to-and-including
    `step`.  Mirrors storage.get_state_at() but self-contained so this
    module has no import-time dependency on storage.
    Row shape: (id, step, timestamp, line_number, function_name,
                variable_name, variable_value, value_type)
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT t1.*
        FROM trace_events t1
        INNER JOIN (
            SELECT variable_name, MAX(step) AS max_step
            FROM trace_events
            WHERE step <= ?
            GROUP BY variable_name
        ) t2
            ON  t1.variable_name = t2.variable_name
            AND t1.step          = t2.max_step
        ORDER BY t1.variable_name ASC
        """,
        (step,),
    )
    return cursor.fetchall()


def _query_event_at_step(conn: sqlite3.Connection, step: int) -> Optional[tuple]:
    """Returns *any* row recorded at exactly `step` (for line / fn / ts)."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM trace_events WHERE step = ? LIMIT 1", (step,)
    )
    return cursor.fetchone()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_total_steps(conn: sqlite3.Connection) -> int:
    """
    Returns the total number of distinct execution steps recorded.
    Step numbers are 1-based in storage; we expose a 0-based count
    so callers can iterate range(get_total_steps(conn)).
    """
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(step) FROM trace_events")
    result = cursor.fetchone()
    if result is None or result[0] is None:
        return 0
    return int(result[0])


def get_variables_for_step(conn: sqlite3.Connection, step: int) -> dict[str, str]:
    """
    Returns the full reconstructed variable state at *step* as a dict
    mapping variable_name -> JSON-serialised value string.

    This is the "reconstruction" stub mentioned in the spec.
    Currently it delegates to the delta-replay query in _query_state_at.
    When the SQLite-integration team wires in proper delta decompression
    they can replace the body of this function.
    """
    rows = _query_state_at(conn, step)
    # row indices: 0=id, 1=step, 2=ts, 3=line, 4=func, 5=var_name, 6=var_val, 7=type
    return {row[5]: row[6] for row in rows}


def get_line_for_step(conn: sqlite3.Connection, step: int) -> int:
    """Returns the source line number active at this step (1-based)."""
    row = _query_event_at_step(conn, step)
    if row is None:
        return 0
    return int(row[3])  # line_number column


def get_function_for_step(conn: sqlite3.Connection, step: int) -> str:
    """Returns the function name active at this step."""
    row = _query_event_at_step(conn, step)
    if row is None:
        return "<module>"
    return row[4]  # function_name column


def get_timestamp_for_step(conn: sqlite3.Connection, step: int) -> str:
    """Returns the ISO-8601 timestamp recorded at this step."""
    row = _query_event_at_step(conn, step)
    if row is None:
        return ""
    return row[2]  # timestamp column


def get_changed_vars_at_step(conn: sqlite3.Connection, step: int) -> set[str]:
    """
    Returns the set of variable names that changed *at* this exact step
    (i.e. the delta introduced by this step).  Used by the UI to
    highlight changed / new variables.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT variable_name FROM trace_events WHERE step = ?", (step,)
    )
    return {row[0] for row in cursor.fetchall()}


def get_source_lines(file_path: str) -> list[str]:
    """
    Reads the target source file from disk and returns its lines
    (without trailing newlines).  Returns [] if the file is not found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


# ---------------------------------------------------------------------------
# Convenience dataclass — snapshot of a single step
# ---------------------------------------------------------------------------

@dataclass
class StepSnapshot:
    """All data needed to render one 'frame' of the debugger UI."""
    step: int
    total_steps: int
    line_number: int
    function_name: str
    timestamp: str
    variables: dict[str, str] = field(default_factory=dict)
    changed_vars: set[str]    = field(default_factory=set)


def get_snapshot(conn: sqlite3.Connection, step: int) -> StepSnapshot:
    """
    Convenience function: fetches everything the UI needs for *step*
    in a single, well-typed object.
    """
    total   = get_total_steps(conn)
    line    = get_line_for_step(conn, step)
    fn      = get_function_for_step(conn, step)
    ts      = get_timestamp_for_step(conn, step)
    vars_   = get_variables_for_step(conn, step)
    changed = get_changed_vars_at_step(conn, step)
    return StepSnapshot(
        step=step,
        total_steps=total,
        line_number=line,
        function_name=fn,
        timestamp=ts,
        variables=vars_,
        changed_vars=changed,
    )
