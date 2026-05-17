"""
uDOS CLI
"""

import click
from .dev_mode import dev


@click.group()
def cli():
    """uDOS CLI for Dev Mode operations."""
    pass


cli.add_command(dev)


if __name__ == '__main__':
    cli()
