import click
import subprocess
import sys


@click.group()
def cli():
    """
    PyChronicle - Python execution analysis and time-travel debugging tool.
    """
    pass


@cli.command()
@click.argument("python_file", type=click.Path(exists=True))
def parse(python_file):
    """
    Parse a Python source file using the existing AST parser.
    """

    click.echo(f"Parsing Python file: {python_file}")

    result = subprocess.run(
        [
            sys.executable,
            "src/ast_parser.py",
            python_file
        ],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        click.echo(result.stdout)
        click.echo("Parsing completed successfully.")
    else:
        click.echo(result.stderr, err=True)
        click.echo("Parsing failed.", err=True)


@cli.command()
def version():
    """
    Display PyChronicle version.
    """

    click.echo("PyChronicle version 1.0.0")


if __name__ == "__main__":
    cli()