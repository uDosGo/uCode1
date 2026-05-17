"""
uDOS Dev Mode CLI
"""

import click
from .commands import start, stop, status, exec


@click.group()
def dev():
    """uDOS Dev Mode operations."""
    pass


dev.add_command(start.start)
dev.add_command(stop.stop)
dev.add_command(status.status)
dev.add_command(exec.exec)
