# PyChronicle – AST-Powered Time-Travel Debugger

## Overview

PyChronicle is a Python-based Time-Travel Debugger designed to help developers understand program execution more effectively. It records execution history, tracks variable changes, and allows users to navigate through execution steps using an interactive Text User Interface (TUI).

The project combines Abstract Syntax Tree (AST) parsing, Python execution tracing, SQLite storage, and delta compression to provide an efficient debugging experience.

---

## Features

- Parse Python source code using the AST module.
- Trace program execution using `sys.settrace`.
- Store execution states in an SQLite database.
- Delta Compression to reduce duplicate variable storage.
- Interactive Text User Interface (TUI) built with Textual.
- Navigate forward and backward through execution steps.
- Jump directly to a specific execution step.
- Command Line Interface (CLI) support.
- Graceful error handling for invalid files.

---

## Technologies Used

- Python 3
- SQLite
- Textual
- AST (Abstract Syntax Tree)
- sys.settrace
- Git & GitHub

---

## Project Structure

```text
PyChronicle/
│
├── sample_code/
│   └── sample_target.py
│
├── src/
│   ├── __init__.py
│   ├── ast_parser.py
│   ├── cli.py
│   ├── data_source.py
│   ├── delta_compression.py
│   ├── parser.py
│   ├── storage.py
│   ├── tracer.py
│   ├── tui_app.py
│   ├── week3_integration.py
│   ├── week3_validation.py
│   ├── WEEK4_INSTALLATION_TEST.md
│   └── WEEK4_PACKAGE_TEST.md
│
├── tests/
├── database/
│
├── .gitignore
├── pychronicle.db
├── pyproject.toml
├── README.md
├── requirements.txt
├── run_debugger.py
├── sample_target.py
└── WEEK4_PACKAGING.md
```

---

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd PyChronicle
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Run the Time-Travel Debugger

```bash
python run_debugger.py sample_target.py
```

### Run the Command Line Interface

```bash
python -m src.cli
```

### Display Version

```bash
python -m src.cli version
```

### Parse a Python File

```bash
python -m src.cli parse sample_target.py
```

---

## Testing Summary

The following functionality was successfully tested during the final review.

| Test Case | Status |
|-----------|--------|
| Application Launch | ✅ Passed |
| Sample File Loading | ✅ Passed |
| Timeline Navigation | ✅ Passed |
| Variable Display | ✅ Passed |
| Go To Step Function | ✅ Passed |
| Quit Function | ✅ Passed |
| Invalid File Handling | ✅ Passed |
| CLI Help Command | ✅ Passed |
| CLI Version Command | ✅ Passed |
| CLI Parse Command | ✅ Passed |

**Overall Result:** All functional tests passed successfully.

---

## Future Enhancements

- Breakpoint support
- Variable history visualization
- Export execution reports
- Search functionality
- Performance improvements for large Python programs
- Additional UI customization options

---

## Project Team

| Name     | Role |
|----------|------|
| Darsha   | Team Member |
| Samhitha | Team Member |
| Shankar  | Team Member |

---

## Acknowledgements

This project was developed as part of an academic software engineering project to demonstrate Python execution tracing, AST parsing, delta compression, SQLite-based execution storage, and time-travel debugging concepts.

---
