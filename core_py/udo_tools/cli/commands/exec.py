import click
import json
import sys
import os

# Add the udo directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from udo.cli.utils.state import check_dev_mode
from udo.core import execute_dev_action


@click.command()
@click.argument('tool')
@click.option('--args', default='{}', help='JSON arguments for the tool')
def exec(tool, args):
    """Execute a DevOnly action."""
    if not check_dev_mode():
        click.echo("❌ Dev Mode not active. Use `udo dev start`.", err=True)
        return

    try:
        arguments = json.loads(args)
    except json.JSONDecodeError:
        click.echo("❌ Invalid JSON arguments.", err=True)
        return

    try:
        result = execute_dev_action(tool, arguments)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"❌ Error executing {tool}: {str(e)}", err=True)
