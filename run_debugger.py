"""
run_debugger.py
===============
PyChronicle — Time-Travel Debugger
Entry-point script (run from the project root).

Usage
-----
  python run_debugger.py <target_script.py>

Examples
--------
  python run_debugger.py sample_target.py
  python run_debugger.py sample_code/sample_target_v2.py

What it does
------------
1. Validates the target file exists.
2. Runs the sys.settrace-based tracer on it (in-memory SQLite DB).
3. Opens the PyChronicle TUI so you can scrub through execution steps.

To wire in a persistent DB or a pre-recorded session, replace the call
to `tracer.run_with_trace()` with your own connection and pass it to
PyChronicleApp(conn=..., file_path=...).
"""

from __future__ import annotations

import os
import sys

# ── Resolve paths ────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.join(_ROOT, "src")

# Make sure both the project root and src/ are on the path
for _p in (_ROOT, _SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Imports (after path setup) ────────────────────────────────────────────────
import tracer       # src/tracer.py
import data_source as ds  # src/data_source.py
from tui_app import PyChronicleApp  # src/tui_app.py


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        print("ERROR: No target script specified.\n")
        print("Usage: python run_debugger.py <target_script.py>")
        sys.exit(1)

    target = sys.argv[1]

    # Resolve relative to CWD
    if not os.path.isabs(target):
        target = os.path.join(os.getcwd(), target)

    if not os.path.exists(target):
        print(f"ERROR: File not found: {target}")
        sys.exit(1)

    if not target.endswith(".py"):
        print(f"WARNING: '{target}' does not look like a Python file — proceeding anyway.")

    # ── Trace ────────────────────────────────────────────────────────────────
    print(f"\n  PyChronicle — Time-Travel Debugger")
    print(f"  ─────────────────────────────────────")
    print(f"  Target : {target}")
    print(f"  Tracing… ", end="", flush=True)

    conn = tracer.run_with_trace(target)
    total = ds.get_total_steps(conn)

    print(f"done.  {total} step(s) recorded.")

    if total == 0:
        print("\n  No execution steps were captured.")
        print("  The target script may have no traceable statements.")
        sys.exit(0)

    print(f"  Launching TUI…\n")

    # ── Launch TUI ───────────────────────────────────────────────────────────
    app = PyChronicleApp(conn=conn, file_path=target)
    app.run()


if __name__ == "__main__":
    main()
