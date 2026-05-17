import click
import sys
import os

# Add the udo directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from udo.cli.utils.state import enable_dev_mode
from udo.cli.utils.safety import confirm_action


@click.command()
@click.option('--dev-pass', default=None, help='Optional dev mode password')
def start(dev_pass):
    """Enable Dev Mode."""
    if not confirm_action("Enable Dev Mode? This exposes advanced tools."):
        return

    try:
        enable_dev_mode(dev_pass)
        click.echo("✅ Dev Mode activated.")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
