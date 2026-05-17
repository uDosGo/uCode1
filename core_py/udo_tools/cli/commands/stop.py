import click
import sys
import os

# Add the udo directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from udo.cli.utils.state import disable_dev_mode


@click.command()
def stop():
    """Disable Dev Mode."""
    disable_dev_mode()
    click.echo("✅ Dev Mode deactivated.")
