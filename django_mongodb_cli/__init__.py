import click
import sys

from .app import app
from .proj import proj
from .repo import repo


def get_help_text():
    help_text = """
    Django MongoDB CLI
    """
    return f"\n\n{help_text.strip()}\n\nSystem executable:\n\n{sys.executable}\n"


@click.group(help=get_help_text())
def cli():
    """Django MongoDB CLI"""


cli.add_command(app)
cli.add_command(proj)
cli.add_command(repo)
