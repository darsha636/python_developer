# Week 4 Package Build and Verification

## Package Build

PyChronicle was built using the Python build module.

Command:

    python -m build

The build generated:

- Wheel distribution
- Source distribution

## Installation Verification

The generated wheel was installed using pip.

Command:

    pip install dist/pychronicle-1.0.0-py3-none-any.whl

## CLI Verification

The following commands were tested:

    pychronicle --help

    pychronicle version

    pychronicle parse sample_target.py

## Result

The generated PyChronicle package installed successfully.

The installed CLI successfully executed the existing AST parser and produced the expected variable and expression information.

## Status

PASS