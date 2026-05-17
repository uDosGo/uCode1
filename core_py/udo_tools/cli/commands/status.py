import click
import json
import sys
import os

# Add the udo directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from udo.cli.utils.state import check_dev_mode, get_dev_config


@click.command()
def status():
    """Check Dev Mode status."""
    if not check_dev_mode():
        click.echo(json.dumps({"dev_mode": False}))
        return

    config = get_dev_config()
    click.echo(json.dumps({
        "dev_mode": True,
        "password_protected": "password" in config
    }))
