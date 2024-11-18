import click
import os
import subprocess


from .utils import get_management_command


@click.command()
@click.argument("name", required=False)
def startapp(name):
    """Run startapp command with the template from src/django-mongodb-app."""

    click.echo("Running startapp.")
    command = get_management_command("startapp")
    subprocess.run(
        command
        + [
            name,
            "--template",
            os.path.join("src", "django-project-templates", "app_template"),
        ],
    )
