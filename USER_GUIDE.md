# PyChronicle User Guide

## Introduction

PyChronicle is a Python-based Time-Travel Debugger that helps users analyze Python program execution by recording execution history and allowing navigation through each execution step.

---

# System Requirements

- Python 3.x
- Windows/Linux/macOS
- Git (optional)

---

# Installation

1. Clone the repository.

```bash
git clone <repository-url>
```

2. Open the project folder.

```bash
cd PyChronicle
```

3. Install the required dependencies.

```bash
pip install -r requirements.txt
```

---

# Running the Application

Run the debugger using:

```bash
python run_debugger.py sample_target.py
```

---

# Using the Command Line Interface

Display available commands:

```bash
python -m src.cli
```

Display version:

```bash
python -m src.cli version
```

Parse a Python file:

```bash
python -m src.cli parse sample_target.py
```

---

# Keyboard Shortcuts

| Key | Function |
|------|----------|
| → | Next execution step |
| ← | Previous execution step |
| g | Jump to a specific step |
| q | Quit the application |

---

# Error Handling

If a file does not exist:

```bash
python run_debugger.py abc.py
```

The application displays an error message instead of crashing.

---

# Features

- AST Parsing
- Python Execution Tracing
- SQLite Storage
- Delta Compression
- Interactive TUI
- CLI Support

---

# Troubleshooting

### Module Not Found

Install dependencies:

```bash
pip install -r requirements.txt
```

### File Not Found

Verify the file path before running the debugger.

---

# Conclusion

PyChronicle provides an interactive environment for analyzing Python program execution and understanding variable changes over time.