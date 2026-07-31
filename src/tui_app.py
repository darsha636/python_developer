"""
tui_app.py
==========
PyChronicle — Time-Scrubbing Debugger UI
Built with Textual (https://textual.textualize.io/)

Layout (three panels, horizontal split):
  ┌──────────────────────┬──────────────────┬────────────────────┐
  │   SOURCE CODE         │   TIMELINE       │   VARIABLES        │
  │   (scrollable)        │   scrub-bar      │   name / value     │
  │   ▶ active line       │   step counter   │   changed=yellow   │
  │                       │   fn / timestamp │   new=green        │
  └──────────────────────┴──────────────────┴────────────────────┘

Keyboard bindings:
  ← / h        Step back 1
  → / l        Step forward 1
  Page Up      Step back 10
  Page Down    Step forward 10
  Home         Jump to first step
  End          Jump to last step
  g            Go to step (input prompt)
  q / Ctrl+C   Quit
"""

from __future__ import annotations

import sqlite3
import sys
import os
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Label, Static
from textual.screen import ModalScreen

# ---------------------------------------------------------------------------
# data_source is the only link to the DB — the UI never touches storage.py
# ---------------------------------------------------------------------------
# Support running as  `python tui_app.py`  from inside src/
_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import data_source as ds
from data_source import StepSnapshot


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Goto-step modal                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GotoStepModal(ModalScreen[Optional[int]]):
    """A small overlay that asks the user for a step number."""

    CSS = """
    GotoStepModal {
        align: center middle;
    }
    GotoStepModal > Vertical {
        background: $surface;
        border: double $accent;
        padding: 1 3;
        width: 40;
        height: auto;
    }
    GotoStepModal Label {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        color: $text-muted;
    }
    GotoStepModal Input {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Jump to step — press Enter or Escape")
            yield Input(placeholder="step number…", id="step_input")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            step = int(event.value)
            self.dismiss(step)
        except ValueError:
            self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Source-code panel                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class SourceView(ScrollableContainer):
    """
    Left panel.  Displays the traced source file with the currently
    active line highlighted and a ▶ gutter indicator.
    Scrolls automatically to keep the active line visible.
    """

    DEFAULT_CSS = """
    SourceView {
        width: 2fr;
        height: 100%;
        border: solid $primary-darken-2;
        padding: 0;
        overflow-y: auto;
        overflow-x: auto;
        scrollbar-gutter: stable;
    }
    SourceView > Static {
        width: 100%;
        padding: 0 1;
    }
    """

    active_line: reactive[int] = reactive(0)

    def __init__(self, source_lines: list[str], **kwargs) -> None:
        super().__init__(**kwargs)
        self._source_lines = source_lines

    def compose(self) -> ComposeResult:
        yield Static("", id="source_content")

    def on_mount(self) -> None:
        self._render_source()

    def watch_active_line(self, _old: int, _new: int) -> None:
        self._render_source()
        self._scroll_to_active()

    def _render_source(self) -> None:
        lines: list[str] = []
        if not self._source_lines:
            lines.append("[dim]  (no source file loaded)[/dim]")
        else:
            for i, src_line in enumerate(self._source_lines, start=1):
                # Escape Rich markup in source code
                escaped = src_line.replace("[", "\\[")
                num = f"{i:4}"
                if i == self.active_line:
                    lines.append(
                        f"[bold yellow]▶[/bold yellow][bold reverse] {num} │ {escaped} [/bold reverse]"
                    )
                else:
                    lines.append(f"[dim]  {num} │[/dim] {escaped}")
        content = self.query_one("#source_content", Static)
        content.update("\n".join(lines))

    def _scroll_to_active(self) -> None:
        if self.active_line <= 0:
            return
        # Approximate: each rendered line is 1 cell tall.
        # Scroll so the active line is roughly in the centre.
        target = max(0, self.active_line - 10)
        self.scroll_to(y=target, animate=True)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Timeline / scrubber panel                                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TimelinePanel(Static):
    """
    Centre panel.
    Shows an ASCII scrub-bar, step counter, function name and timestamp.
    """

    DEFAULT_CSS = """
    TimelinePanel {
        width: 24;
        height: 100%;
        border: solid $accent-darken-2;
        padding: 1 2;
        color: $text;
    }
    """

    snapshot: reactive[Optional[StepSnapshot]] = reactive(None)

    def render(self) -> str:
        snap = self.snapshot
        if snap is None:
            return "[dim]Loading…[/dim]"

        total = snap.total_steps
        step  = snap.step

        # ── Scrub bar ──────────────────────────────────────────
        bar_len = 18
        if total > 1:
            pos = int((step / (total - 1)) * (bar_len - 1))
        else:
            pos = 0
        bar = ["─"] * bar_len
        bar[pos] = "●"
        pct = int((step / max(total - 1, 1)) * 100)
        scrub = f"[{''.join(bar)}]"

        # ── Timestamp (time portion only) ──────────────────────
        ts = snap.timestamp
        time_part = ts[11:19] if len(ts) >= 19 else ts

        # ── Function breadcrumb ────────────────────────────────
        fn = snap.function_name or "<module>"

        # ── Compose output ─────────────────────────────────────
        lines = [
            "[bold $accent]⏱  TIMELINE[/bold $accent]",
            "",
            f"[bold]{scrub}[/bold]",
            f"[dim]{pct:3d}%[/dim]",
            "",
            f"[bold]Step[/bold]",
            f"  [cyan]{step:>4}[/cyan] [dim]/ {total - 1}[/dim]",
            "",
            f"[bold]Line[/bold]",
            f"  [green]{snap.line_number}[/green]",
            "",
            f"[bold]Function[/bold]",
            f"  [magenta]{fn}[/magenta]",
            "",
            f"[bold]Time[/bold]",
            f"  [dim]{time_part}[/dim]",
            "",
            "─" * (bar_len + 2),
            "",
            "[dim]  ← →  step[/dim]",
            "[dim]  PgUp/Dn  ×10[/dim]",
            "[dim]  Home/End jump[/dim]",
            "[dim]  g  goto step[/dim]",
            "[dim]  q  quit[/dim]",
        ]
        return "\n".join(lines)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Variables panel                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class VariablesPanel(Static):
    """
    Right panel.
    Shows the full reconstructed variable state with colour coding:
      • [green]   variable that is NEW at this step
      • [yellow]  variable whose value CHANGED at this step
      • [white]   unchanged variable
    """

    DEFAULT_CSS = """
    VariablesPanel {
        width: 1fr;
        height: 100%;
        border: solid $success-darken-2;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    snapshot: reactive[Optional[StepSnapshot]] = reactive(None)
    prev_vars: dict[str, str] = {}

    def render(self) -> str:
        snap = self.snapshot
        if snap is None:
            return "[dim]Loading…[/dim]"

        lines = [
            "[bold $success]🔍 VARIABLES[/bold $success]",
            f"[dim]  at step {snap.step}[/dim]",
            "",
        ]

        if not snap.variables:
            lines.append("[dim]  (none yet)[/dim]")
        else:
            # Header row
            name_w = max((len(k) for k in snap.variables), default=4)
            name_w = max(name_w, 4)
            lines.append(
                f"[bold dim]  {'NAME':<{name_w}}  VALUE[/bold dim]"
            )
            lines.append(f"[dim]  {'─' * name_w}  {'─' * 20}[/dim]")

            for var_name, var_val in sorted(snap.variables.items()):
                is_changed = var_name in snap.changed_vars
                is_new     = is_changed and var_name not in self.prev_vars

                # Truncate very long values
                display_val = var_val if len(var_val) <= 36 else var_val[:33] + "…"
                escaped_name = var_name.replace("[", "\\[")
                escaped_val  = display_val.replace("[", "\\[")

                if is_new:
                    row = (
                        f"[bold green]✦ {escaped_name:<{name_w}}[/bold green]"
                        f"  [green]{escaped_val}[/green]"
                    )
                elif is_changed:
                    row = (
                        f"[bold yellow]● {escaped_name:<{name_w}}[/bold yellow]"
                        f"  [yellow]{escaped_val}[/yellow]"
                    )
                else:
                    row = (
                        f"[dim]  {escaped_name:<{name_w}}[/dim]"
                        f"  {escaped_val}"
                    )
                lines.append("  " + row)

        # Legend
        lines += [
            "",
            "[dim]─────────────[/dim]",
            "[bold green]✦ new[/bold green]   [bold yellow]● changed[/bold yellow]",
        ]
        return "\n".join(lines)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Main App                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class PyChronicleApp(App):
    """
    PyChronicle — Time-Travel Debugger TUI.

    Accepts:
        conn        : sqlite3.Connection  (from tracer / storage)
        file_path   : str                 (target source file for display)
    """

    TITLE = "PyChronicle — Time-Travel Debugger"
    SUB_TITLE = "Scrub through execution history"

    CSS = """
    Screen {
        layout: horizontal;
        background: $background;
    }

    /* Panel title bars */
    .panel-title {
        background: $primary-darken-3;
        color: $text;
        text-align: center;
        height: 1;
        width: 100%;
        text-style: bold;
    }

    /* Override header / footer colours */
    Header {
        background: $primary-darken-3;
        color: $accent;
    }
    Footer {
        background: $primary-darken-3;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("left",      "step_back",    "◀ Back",      show=True),
        Binding("h",         "step_back",    "◀ Back",      show=False),
        Binding("right",     "step_forward", "Forward ▶",   show=True),
        Binding("l",         "step_forward", "Forward ▶",   show=False),
        Binding("pageup",    "step_back_10", "◀◀ ×10",      show=True),
        Binding("pagedown",  "step_fwd_10",  "×10 ▶▶",      show=True),
        Binding("home",      "step_first",   "⏮ First",     show=True),
        Binding("end",       "step_last",    "⏭ Last",      show=True),
        Binding("g",         "goto_step",    "Go to step",  show=True),
        Binding("q",         "quit",         "Quit",        show=True),
    ]

    current_step: reactive[int] = reactive(0)

    def __init__(
        self,
        conn: sqlite3.Connection,
        file_path: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._conn      = conn
        self._file_path = file_path
        self._total     = ds.get_total_steps(conn)
        self._source    = ds.get_source_lines(file_path) if file_path else []
        # Track previous variable state for diff highlighting
        self._prev_vars: dict[str, str] = {}

    # ── Compose ────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            # Left: source code
            yield SourceView(self._source, id="source_view")
            # Centre: timeline
            yield TimelinePanel(id="timeline_panel")
            # Right: variables
            yield VariablesPanel(id="vars_panel")
        yield Footer()

    # ── Lifecycle ──────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self.sub_title = (
            f"{os.path.basename(self._file_path)} — "
            f"{self._total} step{'s' if self._total != 1 else ''}"
            if self._file_path
            else f"{self._total} step{'s' if self._total != 1 else ''}"
        )
        if self._total == 0:
            self.notify(
                "No execution steps found in the database.",
                severity="warning",
                timeout=5,
            )
            return
        self._refresh_panels()

    # ── Reactive watcher ───────────────────────────────────────────────────

    def watch_current_step(self, _old: int, new: int) -> None:
        self._refresh_panels()

    # ── Panel refresh ──────────────────────────────────────────────────────

    def _refresh_panels(self) -> None:
        """Fetch snapshot for the current step and push to all panels."""
        step = self.current_step
        snap = ds.get_snapshot(self._conn, step)

        # Inject previous-variable dict so the Variables panel can diff
        vars_panel = self.query_one("#vars_panel", VariablesPanel)
        vars_panel.prev_vars = dict(self._prev_vars)
        vars_panel.snapshot  = snap

        # Source panel
        source_view = self.query_one("#source_view", SourceView)
        source_view.active_line = snap.line_number

        # Timeline panel
        timeline = self.query_one("#timeline_panel", TimelinePanel)
        timeline.snapshot = snap

        # Update previous vars AFTER rendering
        self._prev_vars = dict(snap.variables)

    # ── Actions ────────────────────────────────────────────────────────────

    def action_step_back(self) -> None:
        if self.current_step > 0:
            self._prev_vars = ds.get_variables_for_step(
                self._conn, self.current_step - 1
            ) if self.current_step > 1 else {}
            self.current_step -= 1

    def action_step_forward(self) -> None:
        if self.current_step < self._total - 1:
            self.current_step += 1

    def action_step_back_10(self) -> None:
        new = max(0, self.current_step - 10)
        if new != self.current_step:
            self._prev_vars = (
                ds.get_variables_for_step(self._conn, new - 1) if new > 0 else {}
            )
            self.current_step = new

    def action_step_fwd_10(self) -> None:
        new = min(self._total - 1, self.current_step + 10)
        self.current_step = new

    def action_step_first(self) -> None:
        self._prev_vars = {}
        self.current_step = 0

    def action_step_last(self) -> None:
        if self._total > 0:
            self.current_step = self._total - 1

    def action_goto_step(self) -> None:
        """Show the goto-step modal."""
        def _handle(result: Optional[int]) -> None:
            if result is not None:
                target = max(0, min(self._total - 1, result))
                self._prev_vars = (
                    ds.get_variables_for_step(self._conn, target - 1)
                    if target > 0
                    else {}
                )
                self.current_step = target

        self.push_screen(GotoStepModal(), _handle)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Stand-alone entry point (for quick dev testing)                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    # Allow:  python tui_app.py [target_file.py]
    # When run without args, uses a built-in demo trace.
    import sys
    import os

    # We need storage + tracer from the same directory
    _here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, _here)

    import storage  # type: ignore
    import tracer   # type: ignore

    if len(sys.argv) >= 2:
        target = sys.argv[1]
    else:
        # Fall back to the sample target relative to the project root
        _project_root = os.path.dirname(_here)
        target = os.path.join(_project_root, "sample_code", "sample_target_v2.py")

    if not os.path.exists(target):
        print(f"[error] File not found: {target}")
        sys.exit(1)

    print(f"Tracing '{target}'…  (this may take a moment)")
    conn = tracer.run_with_trace(target)
    total = ds.get_total_steps(conn)
    print(f"Recorded {total} step(s).  Launching TUI…")

    app = PyChronicleApp(conn=conn, file_path=target)
    app.run()
